# chatbot_for_UI.py — Streamlit 전용 사본 (fixed)
# 변경 요약
# - 모델 단일 생성 (secrets/env 지원)
# - generate()에 컨텍스트 실제 주입
# - hallucinating → rewrite_query로 분기 (자기호출 제거)
# - Chroma 초기 문서 등록 (없으면 추가)
# - judge 관련 프롬프트 문장 보정
# - Streamlit 재호출용 엔트리포인트 유지

import os
try:
    import streamlit as st
except Exception:
    st = None

# ===== ❶ OPENAI 키 =====
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or (st.secrets.get("OPENAI_API_KEY") if st else None)
if OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# ===== 공용 import =====
import sys
import logging
import json
import uuid
from datetime import datetime
from typing import Literal, TypedDict, List, Dict

from dotenv import load_dotenv, find_dotenv
import pandas as pd
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain.retrievers import EnsembleRetriever

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.errors import GraphRecursionError

# ===== 경로/환경 =====
THIS_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.normpath(os.path.join(THIS_DIR, "..", "Chatbot_ver2"))
load_dotenv(find_dotenv())

# ===== 로깅 =====
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("chatbot_for_UI")

# ===== 로그 저장 디렉토리 =====
LOG_DIR = os.path.join(BASE_DIR, "chat_logs")
os.makedirs(LOG_DIR, exist_ok=True)

# ===== 1) 모델: 파일 전체에서 단 한 번만 생성 =====
model = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

# ===== 2) State =====
class State(TypedDict):
    input_msg: str
    generation: str
    documents: List[Document] | List[str]
    source: str
    conversation_count: int
    session_id: str
    original_msg: str
    translated_response: str
    route: str
    gen_attempts: int

# ===== 3) RAG 준비 =====
docs: List[Document] = []
file_path = os.path.join(BASE_DIR, "data", "GodQuestions1.xlsx")
df = pd.read_excel(file_path)

for index, row in df.iterrows():
    content = f"질문: {row['Question_KOR']}\n\n답변: {row['Answer_KOR']}"
    metadata = {
        "source": row["URL_KOR"],
        "category": row["big_title_kor"],
        "row_number": int(index) + 1,
    }
    docs.append(Document(page_content=content, metadata=metadata))

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
chroma_dir = os.path.join(BASE_DIR, "chroma_db")
chroma_db = Chroma(embedding_function=embeddings, persist_directory=chroma_dir)

# 처음엔 빈 컬렉션일 수 있으니 한 번만 추가
if not chroma_db._collection.count():  # type: ignore[attr-defined]
    chroma_db.add_documents(docs)

chroma_retriever = chroma_db.as_retriever(search_kwargs={"k": 2})
bm25_retriever = BM25Retriever.from_documents(docs)
ensemble_retriever = EnsembleRetriever(
    retrievers=[chroma_retriever, bm25_retriever],
    weights=[0.5, 0.5],
)

# ===== 4) 로깅 =====
def save_log(state: State, response, route: str):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": state.get("session_id", "unknown"),
        "original_message": state.get("original_msg", state.get("input_msg", "")),
        "translated_input": state.get("input_msg", ""),
        "bot_response": response,
        "translated_response": state.get("translated_response", response),
        "conversation_count": state.get("conversation_count", 0),
        "route": route,
    }
    log_file = os.path.join(LOG_DIR, f"chat_log_{state.get('session_id','unknown')}.json")
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            json.dump(log_entry, f, ensure_ascii=False)
            f.write("\n")
    except Exception as e:
        logger.error("Failed to save log: %s", e)

# ===== 5) 번역 노드 =====
def translate_persian_to_english(state: State) -> State:
    input_msg = state["input_msg"]
    system = (
        "You are an expert translator. Translate Persian to English accurately. "
        "If input is not Persian (already English or other), return it unchanged."
    )
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", "{input_msg}")])
    chain = prompt | model | StrOutputParser()
    translated_msg = chain.invoke({"input_msg": input_msg})
    return {
        "original_msg": input_msg,
        "input_msg": translated_msg,
        "session_id": state.get("session_id", "unknown"),
        "conversation_count": state.get("conversation_count", 0),
    }

def translate_english_to_persian(state: State) -> State:
    generation = state.get("generation", "")
    route = state.get("route", "unknown")
    system = (
        "You are an expert translator. Translate the English text to Persian accurately. "
        "If the input is empty/None, return nothing."
    )
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", "{generation}")])
    chain = prompt | model | StrOutputParser()
    translated_response = chain.invoke({"generation": generation}) if generation else ""
    save_log(state, translated_response, route)
    return {
        "input_msg": state.get("input_msg", ""),
        "generation": generation,
        "translated_response": translated_response,
        "documents": state.get("documents", []),
        "source": state.get("source", ""),
        "conversation_count": state.get("conversation_count", 0),
        "session_id": state.get("session_id", "unknown"),
        "original_msg": state.get("original_msg", state.get("input_msg", "")),
        "route": route,
    }

# ===== 6) 라우팅 =====
def router(state: State) -> State:
    state["conversation_count"] = state.get("conversation_count", 0) + 1
    return state

class RouteQuery(BaseModel):
    router: Literal["block", "rag", "default"] = Field(
        description="Choose one: block, rag, or default."
    )

def route_query(state: State) -> Literal["block", "rag", "default"]:
    model_with_structured_output = model.with_structured_output(RouteQuery)
    input_msg = state["input_msg"]
    conversation_count = state.get("conversation_count", 0)
    system = """
You classify a user message into: block, rag, or default.

- block: profanity, curses, spam/ads, inappropriate sexual content, threats.
- default: general life/relationship/stress topics (non-faith).
- rag: faith-related, religion, Bible, Christian theology.

If conversation_count > 3 and it is default, route to block to limit non-faith discussions.
Return exactly one word: block, rag, or default.
"""
    prompt_router = ChatPromptTemplate.from_messages([("system", system), ("human", "{input_msg}")])
    out = (prompt_router | model_with_structured_output).invoke({"input_msg": input_msg})
    if out.router == "block" or (out.router == "default" and conversation_count > 3):
        return "block"
    elif out.router == "rag":
        return "rag"
    else:
        return "default"

def node_default_responser(state: State) -> State:
    input_msg = state["input_msg"]
    conversation_count = state.get("conversation_count", 0)
    system = """
You are a gentle Christian counselor for Muslim audiences. Be brief (1–2 sentences), warm, and hopeful.
If the chat doesn't move toward faith after a few turns, start wrapping up kindly.
"""
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", "{input_msg}")])
    result = (prompt | model | StrOutputParser()).invoke({"input_msg": input_msg})
    if conversation_count > 3:
        result += "\n\nI appreciate our chat! If you have questions about faith or spirituality, I'm here to help."
    return {
        "input_msg": input_msg,
        "source": "default",
        "generation": result,
        "conversation_count": conversation_count,
        "session_id": state.get("session_id", "unknown"),
        "original_msg": state.get("original_msg", input_msg),
        "route": "default",
    }

def node_rag_responser(state: State) -> State:
    input_msg = state["input_msg"]
    documents = ensemble_retriever.invoke(input_msg)
    return {
        "documents": documents,
        "input_msg": input_msg,
        "source": "vectorstore",
        "conversation_count": state.get("conversation_count", 0),
        "session_id": state.get("session_id", "unknown"),
        "original_msg": state.get("original_msg", input_msg),
        "route": "rag",
    }

def node_block_responser(state: State) -> State:
    # 아무 응답도 안 함 (로그만)
    save_log(state, None, "block")
    return {
        "input_msg": state.get("input_msg", ""),
        "generation": None,
        "translated_response": None,
        "conversation_count": state.get("conversation_count", 0),
        "session_id": state.get("session_id", "unknown"),
        "original_msg": state.get("original_msg", state.get("input_msg", "")),
        "route": "block",
    }

def rewrite_query(state: State) -> State:
    input_msg = state["input_msg"]
    documents = state.get("documents", [])
    system = """
You rewrite the user's question to optimize for vectorstore retrieval.
Infer the underlying intent. Keep the meaning; make it concise and specific.
"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", "Here is the initial question:\n\n{question}")
    ])
    new_question = (prompt | model | StrOutputParser()).invoke({"question": input_msg})
    return {
        "documents": documents,
        "input_msg": new_question,
        "conversation_count": state.get("conversation_count", 0),
        "session_id": state.get("session_id", "unknown"),
        "original_msg": state.get("original_msg", input_msg),
        "route": state.get("route", "rag"),
    }

def generate(state: State) -> State:
    input_msg = state["input_msg"]
    documents: List[Document] = state.get("documents", [])
    source = state.get("source", "vectorstore")
    attempts = state.get("gen_attempts", 0) + 1

    # 컨텍스트 문자열로 주입
    ctx = "\n\n---\n\n".join(d.page_content for d in documents) if documents else "NO_CONTEXT"

    system = """You are a wise and compassionate pastor with deep knowledge of the Bible.
Answer ONLY using the provided context. If context is missing/insufficient, say you don't know
and suggest a brief follow-up. Keep it to 1–2 sentences. Speak naturally; not like an AI."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", "Context:\n{context}\n\nQuestion:\n{input_msg}")
    ])
    out = (prompt | model | StrOutputParser()).invoke({"context": ctx, "input_msg": input_msg})

    return {
        "documents": documents,
        "input_msg": input_msg,
        "source": source,
        "generation": out,
        "conversation_count": state.get("conversation_count", 0),
        "session_id": state.get("session_id", "unknown"),
        "original_msg": state.get("original_msg", input_msg),
        "route": state.get("route", "rag"),
        "gen_attempts": attempts,
    }

# ===== 판정기 =====
class Relevancy(BaseModel):
    binary_score: str = Field(description="Are the documents relevant? 'yes' or 'no'.")

def judge_retrieval(state: State) -> State:
    input_msg = state["input_msg"]
    documents = state.get("documents", [])
    judge = model.with_structured_output(Relevancy)
    system = """
You judge whether a retrieved document is relevant to the user's question.
If it shares key terms or close semantics with the question, answer 'yes'; otherwise 'no'.
The aim is to filter out clearly wrong docs, not to be overly strict.
"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", "Document:\n{document}\n\nQuestion:\n{input_msg}")
    ])

    filtered_docs: List[Document] = []
    for doc in documents:
        out = (prompt | judge).invoke({"input_msg": input_msg, "document": doc.page_content})
        if out.binary_score.lower().strip() == "yes":
            filtered_docs.append(doc)

    return {
        "documents": filtered_docs,
        "input_msg": input_msg,
        "conversation_count": state.get("conversation_count", 0),
        "session_id": state.get("session_id", "unknown"),
        "original_msg": state.get("original_msg", input_msg),
        "route": state.get("route", "rag"),
    }

class Factfulness(BaseModel):
    binary_score: str = Field(description="Is the answer grounded in the docs? 'yes' or 'no'.")

class Addressed(BaseModel):
    binary_score: str = Field(description="Does the answer address the question? 'yes' or 'no'.")

def judge_answer(state: State) -> str:
    input_msg = state["input_msg"]
    generation = state.get("generation", "")
    system = "Judge if the answer resolves the user's question. Reply 'yes' or 'no'."
    prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", "Question:\n{q}\n\nAnswer:\n{a}")
    ])
    out = (prompt | model.with_structured_output(Addressed)).invoke({"q": input_msg, "a": generation})
    return out.binary_score

def judge_factfullness(state: State) -> Literal["resolved", "not resolved", "hallucinating"]:
    documents: List[Document] = state.get("documents", [])
    generation = state.get("generation", "")
    # 초과 재시도 방지
    if state.get("gen_attempts", 0) >= 3 and documents:
        return "not resolved"

    system = "Judge if the answer is grounded in the given documents. Reply 'yes' or 'no'."
    prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", "Documents:\n{docs}\n\nAnswer:\n{ans}")
    ])
    docs_text = "\n\n---\n\n".join(d.page_content for d in documents) if documents else ""
    out = (prompt | model.with_structured_output(Factfulness)).invoke({"docs": docs_text, "ans": generation})

    if out.binary_score.lower().strip() == "yes":
        return "resolved" if judge_answer(state).lower().strip() == "yes" else "not resolved"
    else:
        return "hallucinating"

def generate_or_rewrite_query(state: State) -> Literal["generate", "rewrite_query"]:
    return "generate" if state.get("documents") else "rewrite_query"

# ===== 7) 그래프 구성 =====
memory = MemorySaver()
graph = (
    StateGraph(State)
    .add_node("translate_persian_to_english", translate_persian_to_english)
    .add_node("router", router)
    .add_node("node_rag_responser", node_rag_responser)
    .add_node("node_default_responser", node_default_responser)
    .add_node("node_block_responser", node_block_responser)
    .add_node("generate", generate)
    .add_node("judge_retrieval", judge_retrieval)
    .add_node("rewrite_query", rewrite_query)
    .add_node("translate_english_to_persian", translate_english_to_persian)
    .add_edge(START, "translate_persian_to_english")
    .add_edge("translate_persian_to_english", "router")
    .add_conditional_edges("router", route_query, {
        "rag": "node_rag_responser",
        "default": "node_default_responser",
        "block": "node_block_responser",
    })
    .add_edge("node_default_responser", "translate_english_to_persian")
    .add_edge("node_rag_responser", "judge_retrieval")
    .add_conditional_edges("judge_retrieval", generate_or_rewrite_query, {
        "generate": "generate",
        "rewrite_query": "rewrite_query",
    })
    .add_edge("rewrite_query", "router")
    .add_conditional_edges("generate", judge_factfullness, {
        "hallucinating": "rewrite_query",   # ★ 루프 차단
        "resolved": "translate_english_to_persian",
        "not resolved": "rewrite_query",
    })
    .add_edge("translate_english_to_persian", END)
    .add_edge("node_block_responser", END)
    .compile(checkpointer=memory)
)

# ===== 8) Streamlit 연동 =====
_GRAPH = None
_THREAD_ID = None

def _get_graph_once():
    global _GRAPH
    if _GRAPH is None:
        _GRAPH = graph
    return _GRAPH

def _ensure_thread_id():
    global _THREAD_ID
    if _THREAD_ID is None:
        _THREAD_ID = str(uuid.uuid4())
    return _THREAD_ID

def _run_graph_once(input_msg: str, conversation_count: int = 0, session_id: str = "streamlit") -> str:
    g = _get_graph_once()
    thread_id = _ensure_thread_id()

    config = RunnableConfig(configurable={"thread_id": thread_id}, recursion_limit=10)
    inputs = {"input_msg": input_msg, "session_id": session_id, "conversation_count": conversation_count}

    final_state: Dict = {}
    try:
        for output in g.stream(inputs, config):
            for _, value in output.items():
                final_state.update(value)
        return (final_state.get("translated_response")
                or final_state.get("generation")
                or "")
    except Exception as e:
        return f"⚠️ 오류가 발생했어요: {e}"

def build_chain():
    """(message: str, history: List[Dict[str,str]]) -> str callable 반환"""
    _get_graph_once()
    def _caller(message: str, history: List[Dict[str, str]]) -> str:
        conv_cnt = sum(1 for m in history if m.get("role") == "user")
        return _run_graph_once(message, conversation_count=conv_cnt, session_id="streamlit-session")
    return _caller

def answer(message: str, history: List[Dict[str, str]]) -> str:
    """Streamlit이 매 전송마다 호출하는 엔트리포인트(문자열 반환 필수)"""
    try:
        return build_chain()(message, history)
    except Exception as e:
        return f"⚠️ 오류가 발생했어요: {e}"

# ===== 9) 단독 실행 테스트 =====
if __name__ == "__main__":
    def run(input_msg, session_id="unknown"):
        config = RunnableConfig(configurable={"thread_id": str(uuid.uuid4())}, recursion_limit=10)
        inputs = {"input_msg": input_msg, "session_id": session_id, "conversation_count": 0}
        final_state = {}
        try:
            for output in graph.stream(inputs, config):
                for _, value in output.items():
                    final_state.update(value)
            print("Generation:", final_state.get("translated_response", final_state.get("generation", "")))
        except GraphRecursionError:
            print("I couldn't find the answer to your question...")

    sid = str(uuid.uuid4())
    for m in ["오늘 날씨는 어때?", "예수님은 누구신가요?", "이 곳에서 나가"]:
        run(m, sid)