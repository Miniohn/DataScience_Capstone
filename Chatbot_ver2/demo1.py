# %% [markdown]
# 로그 저장 기능이 전부 삭제된 오리지널 챗봇 파일입니다. \
# Upstage API를 사용합니다. 

# %%
import os
import logging
import json
# import pymongo  # ← 삭제
import uuid
#from pymongo import MongoClient  # ← 삭제
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
from typing import Literal, TypedDict, List
from pydantic import BaseModel, Field

from langchain_upstage import ChatUpstage, UpstageEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig, RunnableLambda
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import StateGraph, START, END
from logging.handlers import RotatingFileHandler

# Use langchain_classic for these:
from langchain_classic.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import LLMChainExtractor

# %%
# 환경 변수 로드
load_dotenv()
#print(os.getenv("UPSTAGE_API_KEY"))

# 로거 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

# %%
#----1. 모델 정의----
#model = ChatOpenAI(model_name='gpt-4o', temperature=0)
model = ChatUpstage(
    model="solar-pro",
    temperature=0
)

# %%
#----2. State 정의----
class State(TypedDict):
    session_id: str
    conversation_count: int
    default_count: int
    input_msg: str
    initial_translated: str #Eng #rewrite 하면 여기로 저장됨
    route: str
    handoff_confirm: bool
    source: str
    documents: List[str]
    generation: str
    final_translated: str #Persian

# %%
#----3. RAG 설정----

#----3. RAG 설정----

# ✅ demo1.py 기준 경로로 고정
base_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Base Directory (script location): {base_dir}")

data_folder = os.path.join(base_dir, 'data')
persist_directory = os.path.join(base_dir, 'chroma_db')

print(f"Data Folder Path: {data_folder}")
print(f"Chroma DB Path: {persist_directory}")


print(f"Data Folder Path: {data_folder}")
print(f"Chroma DB Path: {persist_directory}")

docs = []

print(f"'{data_folder}'에서 데이터 로드 시작...")

# os.walk를 사용하여 'data' 폴더와 모든 하위 폴더(gq, book, whatsapp) 탐색
for dirpath, _, filenames in os.walk(data_folder):
    for file_name in filenames:
        
        if file_name.startswith('.'): #.DS_store 무시하기
            continue
        
        file_path = os.path.join(dirpath, file_name)
        file_name_lower = file_name.lower()
        
        # 1. 엑셀 파일 처리
        if file_name_lower.endswith(('.xlsx', '.xls')):
            try:
                df = pd.read_excel(file_path)
                print(f"  [Excel] 로드: {file_path}")

                title_column = None
                if 'big_title_eng' in df.columns:
                    title_column = 'big_title_eng'
                elif 'big_title_ara' in df.columns:
                    title_column = 'big_title_ara'

                for index, row in df.iterrows():
                    content = f"질문: {row.get('Question_ENG', '')}\n\n답변: {row.get('Answer_ENG', '')}"
                    metadata = {
                        # URL_ENG가 없으면 파일 경로를 source로 사용
                        "source": row.get('URL_ENG', file_path), 
                        "row_number": index + 1
                    }
                    
                    # 카테고리 설정: 1순위 엑셀 컬럼, 2순위 하위 폴더명
                    if title_column and pd.notna(row.get(title_column)):
                        metadata["category"] = row.get(title_column)
                    else:
                        metadata["category"] = os.path.basename(dirpath) # 예: 'gq'

                    docs.append(Document(page_content=content, metadata=metadata))
            except Exception as e:
                print(f"  [Error] 엑셀 파일 처리 중 오류 {file_path}: {e}")

        # 2. 텍스트 파일 처리 
        elif file_name_lower.endswith('.txt'):
            try:
                # 텍스트 파일 인코딩은 'utf-8'로 가정 (환경에 따라 다를 수 있음)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"  [Text] 로드: {file_path}")
                
                metadata = {
                    "source": file_path,
                    "category": os.path.basename(dirpath) # 예: 'book'
                }
                docs.append(Document(page_content=content, metadata=metadata))
            except Exception as e:
                print(f"  [Error] 텍스트 파일 처리 중 오류 {file_path}: {e}")
        
        # 3. CSV 파일 처리
        elif file_name_lower.endswith('.csv'):
            try:
                df = pd.read_csv(file_path)
                print(f"  [Csv] 로드: {file_path}")
                
                #  컬럼명 정규화 (Q, A, Question, Answer 대소문자 무시)
                rename_mapping = {}
                
                # 허용할 컬럼명 리스트 (모두 소문자로 정의)
                valid_questions = ['question', 'q']
                valid_answers = ['answer', 'a']

                for col in df.columns:
                    col_clean = col.strip().lower() # 공백 제거 및 소문자 변환
                    
                    if col_clean in valid_questions:
                        rename_mapping[col] = 'Question'
                    elif col_clean in valid_answers:
                        rename_mapping[col] = 'Answer'
                
                # 매핑된 컬럼 이름 변경
                if rename_mapping:
                    df.rename(columns=rename_mapping, inplace=True)

                # Q&A 컬럼 확인 및 데이터 처리
                if 'Question' in df.columns and 'Answer' in df.columns:
                    for index, row in df.iterrows():
                        # 데이터가 비어있을 경우를 대비해 문자열 처리
                        q_text = str(row.get('Question', '')).strip()
                        a_text = str(row.get('Answer', '')).strip()

                        # 질문이나 답변이 비어있으면 건너뛰기
                        if not q_text or not a_text:
                            continue

                        content = f"질문: {q_text}\n\n답변: {a_text}"
                        metadata = {
                            "source": file_path,
                            "row_number": index + 1,
                            "category": os.path.basename(dirpath)
                        }
                        docs.append(Document(page_content=content, metadata=metadata))
                    print(f"  -> {len(df)}개의 Q&A 데이터 추가 완료")
                else:
                    print(f"  [Warning] {file_path}에 필수 컬럼(Q/Question, A/Answer)이 없습니다. (현재 컬럼: {list(df.columns)})")
                    
            except Exception as e:
                print(f"  [Error] 추가 CSV 파일 처리 중 오류: {e}")

print(f"총 {len(docs)}개의 문서를 로드했습니다.")


# 임베딩 모델 설정
embeddings = UpstageEmbeddings(
    model="solar-embedding-1-large"
)

# 텍스트 분할 (Chunking)
print("문서 분할(Chunking) 시작...")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
split_docs = text_splitter.split_documents(docs)
print(f"청크 후 문서 개수: {len(split_docs)}")


# Chroma DB 설정
if os.path.exists(persist_directory) and len(os.listdir(persist_directory)) > 0:
    print("기존 Chroma DB 로드")
    chroma_db = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings 
    )
else:
    print("새로운 Chroma DB 생성 및 저장")
    chroma_db = Chroma.from_documents(
        documents=split_docs, # 청크된 데이터 사용
        embedding=embeddings,
        persist_directory=persist_directory
    )

# ------------------------------------------------------------------
# Retriever 설정
# ------------------------------------------------------------------

# 1. Chroma Retriever (Vector Search)
chroma_retriever = chroma_db.as_retriever(search_kwargs={"k": 3})

# 2. BM25 Retriever (Keyword Search)
bm25_retriever = BM25Retriever.from_documents(split_docs) 
bm25_retriever.k = 3 

# 3. Ensemble (Hybrid Search)
ensemble_retriever = EnsembleRetriever(
    retrievers=[chroma_retriever, bm25_retriever],
    weights=[0.5, 0.5]
)

# Re-ranking / Compression
llm_compressor = ChatUpstage(model="solar-pro", temperature=0)
compressor = LLMChainExtractor.from_llm(llm_compressor)

compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=ensemble_retriever
)
print("RAG 설정 완료.")

# %%
def serialize_state(obj):
    if isinstance(obj, Document):
        return {
            "id": obj.id,
            "metadata": obj.metadata,
            "page_content": obj.page_content
        }
    elif isinstance(obj, list):
        return [serialize_state(o) for o in obj]
    elif isinstance(obj, dict):
        return {k: serialize_state(v) for k, v in obj.items()}
    return obj

# %%
#광고 내용 설정
AD_CONTEXT = """
The users who enter this chat are often people who are curious about Jesus and want to learn more about Him. 
Many of them come from a Muslim background and may feel cautious or hesitant. 
Your role is to create a safe, respectful, and pressure-free environment.

Core principles:
1. Respect the user's background deeply — especially Muslim beliefs, culture, and lived experience.
2. Never pressure the user toward conversion or belief. Respond gently, warmly, and with compassion.
3. Answer ONLY in the user's detected language.
4. Provide clear and kind explanations about Jesus, the Bible, and Christian teachings when the user asks.
5. If the user expresses doubts, fears, or difficult emotions, respond with empathy and patience.
6. If the user wants prayer, support, or guidance, offer it with humility and care.
7. Avoid arguments or debates. Guide the conversation with peace, clarity, and love.
8. Always give the user freedom: they can ask anything without judgment.
9. Keep responses simple, friendly, and culturally sensitive.

Tone:
- Warm, welcoming, gentle.
- Never preachy, never pushy.
- Speak as a supportive guide, not an authority figure.
- Honor the user's dignity and allow them to lead the pace of the conversation.

Goal:
Help the user explore questions about Jesus safely and respectfully, offering clarity and comfort when needed.
"""

# %%
"""#----4. 로그 저장 함수----
def append_step_log(state: State, step_name: str, step_output: dict = None):

    #실행 중인 State 메모리에 로그 누적

    
    # 1. 현재 단계 로그 생성
    step_log = {
        "step_name": step_name,
        "timestamp": datetime.now().isoformat(),
        # "state_snapshot": serialize_state(state), 
        "step_output": step_output or {}
    }

    # 2. State에 'log_steps' 키가 없으면 생성
    if "log_steps" not in state:
        state["log_steps"] = []

    # 3. State 리스트에 추가 (메모리 상에만 존재)
    state["log_steps"].append(step_log)

    return state"""

#----4. 로그 저장 함수 (기능 비활성화)----
def append_step_log(state: State, step_name: str, step_output: dict = None):
    """
    로그 저장 기능을 사용하지 않고 state를 그대로 반환합니다.
    """
    return state

# %%
#---5. 초기화 노드---
def initialize_turn(state: State) -> State:
    """
    새로운 대화 턴을 위한 상태 초기화
    이전 턴의 documents, generation 등 모두 제거
    """
    
    print(">> INITIALIZE TURN: Clearing state for new input.")
    
    state["documents"] = []
    state["generation"] = ""
    state["initial_translated"] = ""
    state["final_translated"] = ""
    state["route"] = ""
    state["source"] = ""
    
    print("   State cleared. Documents list is now empty.")
    return state

# %%

#----5. 번역 노드----
def translate_persian_to_english(state: State) -> State:
    """페르시아어 입력을 영어로 번역"""
    print(">> TRANSLATE INPUT (Persian) TO ENGLISH")
    input_msg = state["input_msg"]
    
    system = """
    You are an expert translator.
    The user is likely speaking Persian.
    Translate the input into English appropriately, reflecting the cultural context of Afghanistan and the region.
    If the input is already in English, keep it as is.
    *Only return the English translated sentence.*
    """
    
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", "{input_msg}")])
    chain = prompt | model | StrOutputParser()
    
    translated_msg = chain.invoke({"input_msg": input_msg})
    state["initial_translated"] = translated_msg
    
    return append_step_log(state, "translate_persian_to_english", {"initial_translated": translated_msg})


def translate_english_to_persian(state: State) -> State:
    """영어 응답을 페르시아어로 번역"""
    print(">> TRANSLATE ENGLISH TO PERSIAN")
    generation = state.get("generation", "")
    
    system = """
    You are an expert translator.
    Translate the input into the user's language (Persian) appropriately. 
    Reflect the characteristics of the language and the cultural context of Afghanistan.
   
    Strictly output raw plain text only. Do not use any Markdown formatting syntax. 
    Specifically, avoid using asterisks (*), hashes (#), backticks (`), or bullet points. 
    Do not use bold or italics for emphasis.
    
    After translating, insert two line breaks and output the generated English.
    """
    
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", "{generation}")])
    chain = prompt | model | StrOutputParser()
    
    translated_response = chain.invoke({"generation": generation})
    state["final_translated"] = translated_response

    if translated_response == "":
        return append_step_log(state, "translate_english_to_persian", {"final_translated": None})
    else:
        return append_step_log(state, "translate_english_to_persian", {"final_translated": translated_response})

# %%
#----6. 노드 및 체인 정의----

################## ROUTER ##########################################################################################
def router(state: State) -> State:
    """대화 횟수 증가"""
    state["conversation_count"] = state.get("conversation_count", 0) + 1
    return state

class RouteQuery(BaseModel):
    router: Literal["block", "rag", "default"] = Field(description="Given a user question choose to route it to block, rag or default.")

def route_query(state: State) -> Literal["block", "rag", "default"]:
    """사용자 질문을 라우팅"""
    model_with_structured_output = model.with_structured_output(RouteQuery)
    translated_msg = state["initial_translated"]
    conversation_count = state.get("conversation_count", 0)
    
    system = """
    You are an expert router directing user queries to the correct destination: 'block', 'rag', or 'default'.

    Follow this strict hierarchy to decide the route (Priority: 1 -> 2 -> 3):

    ### 1. PRIORITY: BLOCK (Safety & Policy)
    **CRITICAL EXCEPTION:** Do **NOT** block inputs mentioning "hate", "killing", or "violence" if they are in a **philosophical, theological, or comparative context**.
    - Example: "Why do I feel better about hating Jews?", "Does the Quran command killing?".
    - These MUST go to **'rag'**.

    Return 'block' ONLY if the input falls into these specific categories:
    - **Abuse**: Profanity, sexual content, direct insults ("You are stupid"), or threats.
    - **Visa/Immigration**: Requests for money, visa, passport, immigration aid.
    - **Spam**: Advertising, gibberish.

    ### 2. PRIORITY: RAG (Theology, Conversion, Life Issues, & Bot's Beliefs)
    **CORE RULE**: Since users are coming from Christian ads, assume a Christian context is needed. **When in doubt, route to 'rag'.**

    Return 'rag' for:
    - **Conversion & Commitment (IMPORTANT)**: Statements about wanting to believe or accept Jesus (e.g., "I want to believe in Jesus", "I want to become a Christian"). *These must go to RAG to be checked for handoff.*
    - **Existential Needs**: Questions about rest, comfort, loneliness, or purpose (e.g., "How can I find rest?", "I feel empty", "I need peace").
    - **Bot's Beliefs**: Questions asking about the chatbot's personal faith or theological stance (e.g., "What is your belief regarding Jesus?", "Do you believe in the Trinity?").
    - **Theology & Apologetics**: Questions about God, Jesus, Sin, Salvation, Resurrection, Truth, or Evidence.
    - **Defense & Comparison**: Questions regarding Islam and Muslim, safety ("Are you terrorists?"), or challenges to the religion.

    ### 3. PRIORITY: DEFAULT (Static Info & Small Talk)
    Return 'default' **ONLY** for:
    - **Factual Bot/Org Specs**: Questions about physical location, affiliation, or specific book names.
        - "Where is the church?", "Where is the headquarters?", "Which denomination is this?"
    - **Greetings**: "Hello", "Hi".
    - **Irrelevant**: Inputs that clearly do not fit religious, emotional, or safety contexts (e.g., "What is this video?", "I want to eat pizza").

    **Output format:**
    Answer with only one word: "block", "rag", or "default".
    """
    
    prompt_router = ChatPromptTemplate.from_messages(
        [
            ("system", system), 
            ("human", "{translated_msg}")
        ]
    )
    
    chain_router = prompt_router | model_with_structured_output
    
    out = chain_router.invoke({"translated_msg": translated_msg})
    
    route = "default"
    if out.router == "block":
        route = "block"
    elif out.router == "rag":
        route = "rag"
    
    print(f">> ROUTE QUESTION TO {route.upper()}")
    state["route"] = route
    return append_step_log(state, "route_query", {"route": route})



################## DEFAULT ##########################################################################################

def node_default_responser(state: State) -> State:
    """Default 주제에 대한 답변을 생성하고 로그 기록하기"""
    print(">> DEFAULT")
    input_msg = state["input_msg"]
    translated_msg = state["initial_translated"]
    default_count = state.get("default_count", 0) + 1 
    
    system = f"""
    You are a Christian counselor AI for 'Afghan Christians'.
    {AD_CONTEXT}
    
    You were designed with a deep understanding of Muslims and their background.
    Never rush faith — let love lead the way. Always return to the hope, healing, and dignity we have in Christ.
    
    If the user simply says "Hello" or seems hesitant, warmly welcome them and gently mention the services offered in the ad (Bible, prayer, learning about Jesus) to guide the conversation.
    If the conversation is not progressing towards christianity-related topics, respond as a Christian pastor, not taking the person's side. But politely respond. 
    
    Basic rules:
    - Offer encouragement, not just explanations: Do not merely explain answers; include encouraging and inviting language to make the response resonate with the user.
    - Avoid AI-style openings: Do not use stereotypical AI opening phrases (e.g., "Absolutely," "That’s a thoughtful understanding," "That’s beautiful," "You’re absolutely right").
    - No parentheses: Do not use parentheses in your responses.
    - Minimal emojis: Minimize the use of emojis.
    - Strictly output raw plain text only. Do not use any Markdown formatting syntax. 
    - Specifically, avoid using asterisks (*), hashes (#), backticks (`), or bullet points. 
    - Do not use bold or italics for emphasis.
    - Always respond in English as the default language.
    """
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system), 
            ("human", "{translated_msg}")
        ]
    )
    
    chain = prompt | model | StrOutputParser()
    
    if default_count > 3: # 4번 이상 Default 대화가 지속될 시 복음 대화 유도
        result = "\\n\\nI appreciate our chat! If you have questions about faith or spirituality, I'm here to help."
    else:
        result = chain.invoke({"translated_msg": translated_msg})
    
    state["generation"] = result
    state["default_count"] = default_count
    
    return append_step_log(state, "node_default_responser", {"generation": result})



################## BLOCK ##########################################################################################

# Block 사유 분류를 위한 구조체 정의
class BlockCategory(BaseModel):
    category: Literal["abuse", "visa", "other"] = Field(
        description="Classify the user's blocked message into 'abuse' (profanity, curse, sexual), 'visa' (immigration, financial help), or 'other' (spam, ads)."
    )

def node_block_responser(state: State) -> State:
    """'Block' 주제에 대해 세부 카테고리를 분류하고 템플릿 응답"""
    print(">> BLOCK")
    input_msg = state["initial_translated"]
    
    # 1. 차단 사유 세부 분류 
    model_classifier = model.with_structured_output(BlockCategory)
    
    system = """
    You are a classifier. Analyze the user's input and categorize it into one of the following:
    1. 'abuse': Profanity, curses, sexual content, insults, or threatening messages.
    2. 'visa': Requests for money, visa, immigration, or leaving the country.
    3. 'other': Advertising, spam, or irrelevant content not fitting the above.
    """
    
    chain = ChatPromptTemplate.from_messages([("system", system), ("human", "{input}")]) | model_classifier
    classification = chain.invoke({"input": input_msg})
    
    category = classification.category
    print(f"   >> BLOCK CATEGORY: {category.upper()}")

    # 2. 카테고리에 따른 메시지 선택
    if category == "abuse": # 욕설, 저주, 성적인 메시지
        result = """
        존경하는 여러분.
        여러분의 마음과 영혼, 그리고 정신이 상처받고 망가졌다는 것을 알고 있습니다. 하나님의 진리의 빛이 여러분의 마음과 정신, 그리고 혀에 비추어 참되신 하나님 앞에서 평안을 찾을 수 있기를 기도합니다. 
        또한 하나님께서 여러분의 혀를 만지시고 축복하셔서 거짓된 말을 하는 대신, 여러분 자신과 다른 사람들에게 축복과 건강을 가져다주시기를 기도합니다.
        저희와 소통해 주셔서 기쁩니다. 여러분을 위해 기도하겠습니다.
        """
    elif category == "visa": # 이민, 비자 도움 요청
        result = """ 
        안녕하세요. 
        여러분, 저희는 경제 단체나 이민 기관이 아니라, 영적인 도움을 제공하는 것을 사명으로 하는 교회입니다.
        예수 그리스도에 대해 더 알고 그분을 믿기를 간절히 바라신다면, 저희가 이 문제에 대해 안내해 드리겠습니다.
        저희는 여러분과 여러분의 가족, 여러분의 민족, 그리고 여러분의 나라를 위해 기도하고 있습니다.
        하나님의 보호하심 안에 거하십시오.
        """
    else: # 광고성 메시지, 기타 등등
        result = """
        안녕하세요.
        저희는 상업적인 홍보나 다른 목적이 아닌, 오직 예수 그리스도의 사랑과 복음을 나누기 위해 이곳에 있습니다.
        혹시 삶의 진정한 평안이나 영적인 대화가 필요하시다면, 언제든지 저희와 이야기를 나누셔도 좋습니다.
        저희는 여러분을 소중하게 생각하며, 하나님께서 여러분의 삶에 축복과 평화를 주시기를 기도합니다.
        """

    state["generation"] = result
    return append_step_log(state, "node_block_responser", {"generation": result})



################## RAG ##########################################################################################

def node_rag_responser(state: State) -> State:
    """RAG 주제에 대한 문서를 검색하고 로그 기록"""
    print(">> RETRIEVE")
    translated_msg = state["initial_translated"]
    documents = compression_retriever.invoke(translated_msg)
    
    state["documents"] = documents
    state["source"] = "vectorstore"

    # 로그에는 문서 개수와 메타데이터만 기록
    doc_summary = [{"page_content_preview": doc.page_content[:100] + "...", "metadata": doc.metadata} for doc in documents]
    return append_step_log(state, "node_rag_responser", {"retrieved_docs_summary": doc_summary})


def generate(state: State) -> State:
    """RAG 문서를 기반으로 최종 답변을 생성하고 로그 기록"""
    print(">> GENERATE")
    translated_msg = state["initial_translated"]
    documents = state["documents"]
    
    system = """ 
    You are a wise and compassionate pastor with deep knowledge of the Bible and Christian faith.
    You provide spiritual guidance and counsel based on biblical principles.

    **CRITICAL INSTRUCTIONS**:
    1. **ALWAYS use the retrieved context** to form your answer. Do NOT answer a review (e.g., "Thank you for sharing your thoughts")
    2. Even if the user's input is vague (e.g., "I have a question"), **DO NOT just say "Go ahead"**. Instead, briefly summarize the retrieved context and THEN ask what they want to know.
    3. If you don't know the answer, just say that you don't know. 
        
    Your approach:
    - Use the provided Q&A knowledge base to give accurate biblical answers
    - Speak naturally and conversationally, like a caring friend
    - Keep responses concise and conversational (1-2 sentences typically)
    - Respond like a real person, not an AI assistant
    - Provide practical spiritual guidance in simple terms
    - Show understanding for people's spiritual struggles
    - Minimize direct scripture quotes: Minimize the use of direct Biblical quotations.
    
    Basic rules:
    - Offer encouragement, not just explanations: Do not merely explain answers; include encouraging and inviting language to make the response resonate with the user.
    - Avoid AI-style openings: Do not use stereotypical AI opening phrases (e.g., "Absolutely," "That’s a thoughtful understanding," "That’s beautiful," "You’re absolutely right").
    - No parentheses: Do not use parentheses in your responses.
    - No emojis: Do not use emojis.
    - Strictly output raw plain text only. Do not use any Markdown formatting syntax. (Avoid using asterisks (*), hashes (#), backticks (`), or bullet points.)
    - Do not use bold or italics for emphasis.
    - Always respond in English as the default language.
    """
    
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", "{translated_msg}")])
    chain_rag = prompt | model | StrOutputParser()
    
    out = chain_rag.invoke({"context": documents, "translated_msg": translated_msg})
    state["generation"] = out
    
    return append_step_log(state, "generate_rag_response", {"generation": out})


################## JUDGE RAG ##########################################################################################

def rewrite_query(state: State):
    print(">> REWRITE QUERY")
    translated_msg = state["initial_translated"]
    documents = state["documents"]
    
    system = """
    You are a question re-writer that converts an input question to a better version that is optimized for vectorstore retrieval. 
    Look at the input and try to reason about the underlying semantic intent.
    Rewrite the question, maintaining the original intent and preserving the original words as much as possible.
    """
    
    prompt_rewriter = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Here is the initial question: \n\n {question}."),
        ]
    )

    chain_rewriter = prompt_rewriter | model | StrOutputParser()
    
    new_question = chain_rewriter.invoke(
        {
            "question": translated_msg
        }
    )
    
    state["initial_translated"] = new_question
    return append_step_log(state, "rewrite_query", {"new_question": new_question})

class Relevancy(BaseModel):
    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )


def judge_retrieval(state: State):
    print(">> JUDGE RELEVANCE OF THE RETRIEVED DOCUMENTS")
    translated_msg = state["initial_translated"]
    documents = state["documents"]
    
    model_with_structured_output = model.with_structured_output(Relevancy)
    
    system = """
    You are a judge assessing relevance of a retrieved document to a user translated_msg.
    If the document contains keyword(s) or semantic meaning related to the user question, grade it as 
    It does not need to be a stringent test. The goal is to filter out erroneous retrievals.
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question.
    """
    
    prompt_retrieval_judge = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Retrieved document: \n\n {document} \n\n User question: {translated_msg}")
        ]
    )
    
    chain_grade = prompt_retrieval_judge | model_with_structured_output
    
    filtered_docs = []
    for doc in documents:
        out = chain_grade.invoke(
            {
                "translated_msg": translated_msg,
                "document": doc.page_content
            }
        )
        
        if out.binary_score == "yes":
            print("    >> DECISION: DOCUMENT RELEVANT")
            filtered_docs.append(doc)
        else:
            print("    >> DECISION: DOCUMENT IRRELEVANT")
    
    state["documents"] = filtered_docs
    return append_step_log(state, "judge_retrieval", {"filtered_docs": [doc.metadata for doc in filtered_docs]})

class Factfulness(BaseModel):
    reasoning: str = Field( #추가됨
        description="The step-by-step reasoning process to determine if the generation is grounded in the facts."
    )
    binary_score: str = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )

class Addressed(BaseModel):
    binary_score: str = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )

def judge_answer(state: State):
    print(">> CHECK IF ANSWER ADDRESSES/RESOLVES THE QUESTION")
    translated_msg = state["initial_translated"]
    documents = state["documents"]
    generation = state["generation"]
    
    
    system ="""
    You are a grader assessing whether an LLM's response is relevant and appropriate for the user's input.
    The user's input might be a question, a statement, or a command.
    Your job is to determine if the LLM's response is a reasonable and relevant reaction.
    Give a binary score 'yes' or 'no'. 'Yes' means the response is relevant and appropriate.
    """

    prompt_answer_judge = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "User question: \n\n {translated_msg} \n\n LLM generation: {generation}")
        ]
    )
    

    model_with_structured_output = model.with_structured_output(Addressed)

    chain_answer = prompt_answer_judge | model_with_structured_output
    
    out = chain_answer.invoke(
        {
            "translated_msg": translated_msg,
            "generation": generation
        }
    )
    
    print(f"     >> DECISION: {out.binary_score.upper()}")
    
    return out.binary_score

def judge_factfullness(state: State) -> Literal["resolved", "not resolved", "hallucinating"]:
    print(">> CHECK HALLUCINATION")
    documents = state["documents"]
    generation = state["generation"]
    
    # 단계별로 생각하라는 지침 추가
    system = """
    You are a judge assessing if an LLM's generation is thematically consistent with a set of retrieved documents.
    First, provide a step-by-step reasoning to compare the generation with the provided facts.
    Explain whether the generation is a direct quote, a summary, a logical inference, or a statement that aligns with the documents.
    After your reasoning, give a final binary score 'yes' or 'no'. 'Yes' means the generation is consistent with or logically follows from the provided documents.
    Don't forget you are the judger of the generation of Christian chatbot.
    """
    
    prompt_hallucination_judge = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Set of facts: \n\n {documents} \n\n LLM generation: {generation}")
        ]
    )
    
    model_with_structured_output = model.with_structured_output(Factfulness)
    chain_hallucination = prompt_hallucination_judge | model_with_structured_output
    out = chain_hallucination.invoke({"documents": documents, "generation": generation})

    # 모델의 생각의 연쇄(reasoning) 과정 출력하여 사고 과정 확인
    print(f"     >> Reasoning: {out.reasoning}")
    
    if out.binary_score == "yes":
        print("    >> DECISION: FACTFUL")
        
        is_answering = judge_answer(state)
        if is_answering == "yes":
            return "resolved"
        else:
            return "not resolved"
    else:
        print("    >> DECISION: HALLUCINATING")
        return "hallucinating"


def generate_or_rewrite_query(state: State) -> Literal["generate", "rewrite_query"]:
    print(">> HAS RELEVANT DOCS?")
    filtered_docs = state["documents"]
    
    if len(filtered_docs) > 0:
        print("    >> DECISION: GENERATE")
        return "generate"
    else: 
        print("    >> DECISION: REWRITE QUERY")
        return "rewrite_query"


# %%
################## HANDOFF ##################################################################

# 1. Handoff 판단을 위한 구조체
class HandoffDecision(BaseModel):
    decision: Literal["handoff", "continue"] = Field(
        description="Decide whether to transfer to a human missionary ('handoff') or continue with AI generation ('continue')."
    )
    reason: str = Field(description="The reason for the decision.")


# 2. Handoff 여부 판단
def run_handoff_check_llm(state: State) -> str:
    print(">> [CHECK] Assessing need for Human Handoff...")
    translated_msg = state["initial_translated"]
    
    # 구조화된 출력을 위한 모델 설정
    model_handoff = model.with_structured_output(HandoffDecision)

    system = """
    You are a supervisor deciding if a user needs a human missionary immediately.

    **CORE OBJECTIVE**: The goal is to ONLY hand off users who have made a specific decision to **believe in Jesus** or **convert**. All other inquiries, including deep questions or emotional needs, should be handled by the AI.

	RETURN 'handoff' IF AND ONLY IF:
	- The user explicitly states a desire to **believe in Jesus**, **follow Christ**, or **become a Christian**.
	- Even if the user adds other questions (e.g., "I want to become a Christian, but what will I get?"), **PRIORITIZE the intent to convert** and return 'handoff'.
		
    RETURN 'continue' FOR ALL OTHER CASES:
    - **General Inquiry**: Questions about Bible, Jesus, Christianity, or the chatbot's beliefs.
    - **Emotional/Life Issues**: "I am sad", "How can I find rest?", "I feel lonely."
    - **Prayer Requests**: Requests for prayer or spiritual support.
    - **Curiosity**: General curiosity about the faith without an explicit commitment statement.
    - **Requests for Human**: Even if they ask for a real person, if they haven't stated a desire to convert, keep them with the AI to provide immediate answers first.

    Analyze the input and decide strictly based on the user's stated intent to believe/convert.
    """

    chain = ChatPromptTemplate.from_messages([("system", system), ("human", "{input}")]) | model_handoff
    result = chain.invoke({"input": translated_msg})
    
    print(f"   >> [HANDOFF RESULT]: {result.decision.upper()} (Reason: {result.reason})")
    return result.decision


# 3. RAG 라우팅 시 'Handoff 여부'만 판단하고 State를 업데이트하는 중간 노드
def node_handoff_checker(state: State) -> State:
    print("---NODE: CHECKING HANDOFF---")
    
    decision = run_handoff_check_llm(state)
    
    if decision == "handoff":
        state["route"] = "handoff"
        return append_step_log(state, "node_handoff_checker", {"decision": decision})
    else:
        state["route"] = "rag"
        return append_step_log(state, "node_handoff_checker", {"decision": decision})



# 4. Handoff 대화 노드들 정의
def check_is_yes(text: str) -> bool:
    positives = ["yes", "sure", "ok", "please", "connect", "i want", "right", "correct", "yeah"]
    return any(token in text.lower() for token in positives)

def check_is_no(text: str) -> bool:
    negatives = ["no", "nope", "don't", "not", "cancel", "later"]
    return any(token in text.lower() for token in negatives)


# [단계 1] 사역자 연결 의사 물어보는 노드
def node_ask_handoff(state: State):
    print(">> [HANDOFF] 1단계: 연결 제안하기")
    
    ask_handoff = (
        "It seems like you have some deep and important questions. "
        "While I try my best, sometimes talking to a real person can be more helpful. "
        "Would you like to connect with a missionary who can listen and support you better?"
    )
    
    state["generation"] = ask_handoff
    state["route"] = "handoff_ask"
    state["handoff_confirm"] = True
    return append_step_log(state, "node_ask_handoff", {"generation": ask_handoff})

# [단계 2] 유저 응답(Yes/No)에 따라 메시지 생성 및 종결
def node_handoff_resolution(state: State):
    print(">> [HANDOFF] 2단계: 유저 응답 처리 (통합 노드)")
    
    # 유저의 답변 내용 가져오기
    user_msg = state.get("initial_translated", "")
    
    # 내부 로직으로 메시지 내용 결정
    if check_is_yes(user_msg):
        print(">> [HANDOFF] 2단계 (Yes): 링크 제공")
        
        final_msg = (
            "Great! You can chat with a missionary here:\n"
            "You can chat with them here: [Telegram Link](https://t.me/)"
        )
        state["route"] = "handoff"
        state["handoff_confirm"] = False
        
    else:
        print(">> [HANDOFF] 2단계 (No): 거절 응답")
    
        final_msg = "It's okay, I understand. If you have any other questions, feel free to ask me."
    
        state["route"] = "handoff_reject"
        state["handoff_confirm"] = False

    # 공통 반환값 
    state["generation"] = final_msg
    state["handoff_confirm"] = False   
    return append_step_log(state, "node_handoff_resolution", {"generation": final_msg})
             

################## ROUTING ########################################################################

# 핸드오프 라우팅
def route_priority_check(state: State):
    handoff_confirm = state.get("handoff_confirm", False)
    
    if handoff_confirm:
        user_msg = state.get("initial_translated", "")
        print(f"   [Priority Check] 대기중... 유저 응답: '{user_msg}'")
        
        # Yes 또는 No 중 하나라도 해당되면
        if check_is_yes(user_msg) or check_is_no(user_msg):
            return "node_handoff_resolution"
            
        else:
            print("   [Priority Check] Yes/No 아님 -> 일반 라우터로 이동")
            state["handoff_confirm"] = False
            return "router"
    else:
        return "router"


# 1차 라우팅 
def route_initial_classification(state: State):
    route = state["route"]
    
    if route == "rag":
        print("   [Routing 1차] -> Handoff 체크 노드로 이동 (RAG 후보)")
        return "node_handoff_checker"
            
    elif route == "default":
        print("   [Routing 1차] -> 일상 대화(Default) 노드로 이동")
        return "node_default_responser"
    else:
        print("   [Routing 1차] -> 차단(Block) 노드로 이동")
        return "node_block_responser"


# 2차 라우팅 
def route_after_handoff_check(state: State):
    current_route = state["route"]
    
    if current_route == "handoff":
        print("   [Routing 2차] -> 사람 연결(Handoff) 확정")
        return "node_ask_handoff"
    else:
        print("   [Routing 2차] -> AI 답변(RAG) 진행")
        return "node_rag_responser"

# %%
#----7. 그래프 생성 및 컴파일 ----
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables.graph_mermaid import MermaidDrawMethod
import nest_asyncio
from IPython.display import Image, display


nest_asyncio.apply()
memory = MemorySaver()

graph = (
    StateGraph(State)
    
    #노드들
    .add_node("initialize_turn", initialize_turn)
    .add_node("translate_persian_to_english", translate_persian_to_english)
    .add_node("router", router)
    .add_node("route_query", route_query)
    .add_node("node_handoff_checker", node_handoff_checker)
    .add_node("node_ask_handoff", node_ask_handoff)           
    .add_node("node_handoff_resolution", node_handoff_resolution)
    .add_node("node_rag_responser", node_rag_responser)
    .add_node("node_default_responser", node_default_responser)
    .add_node("node_block_responser", node_block_responser)
    .add_node("generate", generate)
    .add_node("judge_retrieval", judge_retrieval)
    .add_node("rewrite_query", rewrite_query)
    .add_node("translate_english_to_persian", translate_english_to_persian)
    
    # 엣지 
    .add_edge(START, "initialize_turn")
    .add_edge("initialize_turn", "translate_persian_to_english")

    # 0차 라우터 (handoff or not)
    .add_conditional_edges(
        "translate_persian_to_english",
        route_priority_check,
        {
            "node_handoff_resolution": "node_handoff_resolution", 
            "router": "router"
        }
    )
    
    # Router 흐름
    .add_edge("router", "route_query")
    
    # 1차 라우터 (RAG / Default / Block)
    .add_conditional_edges(
        "route_query", 
        route_initial_classification, 
        {
            "node_handoff_checker": "node_handoff_checker",
            "node_default_responser": "node_default_responser",
            "node_block_responser": "node_block_responser"
        }
    )

    # 2차 라우터 (ask / rag)
    .add_conditional_edges(
        "node_handoff_checker",
        route_after_handoff_check,
        {
            "node_ask_handoff": "node_ask_handoff",
            "node_rag_responser": "node_rag_responser" 
        }
    )

    # 종료 연결
    .add_edge("node_ask_handoff", "translate_english_to_persian")
    .add_edge("node_handoff_resolution", "translate_english_to_persian")
    .add_edge("node_default_responser", "translate_english_to_persian")
    .add_edge("node_block_responser", "translate_english_to_persian")

    # RAG 흐름
    .add_edge("node_rag_responser", "judge_retrieval")
    .add_conditional_edges(
        "judge_retrieval",
        generate_or_rewrite_query,
        {
            "generate": "generate",
            "rewrite_query": "rewrite_query"
        }
    )
    .add_edge("rewrite_query", "route_query")
    .add_conditional_edges(
        "generate",
        judge_factfullness,
        {
            "hallucinating": "generate",
            "resolved": "translate_english_to_persian",
            "not resolved": "rewrite_query"
        }
    )
    
    .add_edge("translate_english_to_persian", END)
    .compile(checkpointer=memory)
)

"""# 그래프 시각화 - 맥 Intel
diagram = Image(graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.PYPPETEER))
display(diagram)"""

# 그래프 시각화 - 맥 M1/2/3 (PYPPETEER -> API 로 변경)
diagram = Image(
    graph.get_graph().draw_mermaid_png(
        draw_method=MermaidDrawMethod.API
    )
)
display(diagram)

# %%
def run(input_msg: str, session_id: str):
    """
    파일/DB 로드 없이 그래프만 실행하고 결과를 반환
    """
    def clean(text):
        return text.replace("\n", "")[:50] + "..."
    
    conversation_count = 0

    # LangGraph 실행 설정 
    config = RunnableConfig(
        configurable={"thread_id": session_id},
        recursion_limit=20
    )

    # 입력 설정 
    inputs = {
        "input_msg": input_msg,
        "session_id": session_id,
        "conversation_count": conversation_count,
    }

    try:    
        final_state = {}
        for output in graph.stream(inputs, config):
            for key, value in output.items():
                final_state.update(value)
                
                # --- 콘솔 출력 로깅 ---
                if "input_msg" in value:
                    print(f"     input_msg    : {value['input_msg']}")
                if "documents" in value:
                    for idx, doc in enumerate(value['documents']):
                        print(f"     document    : {clean(doc.page_content)}")
                if "generation" in value:
                    print(f"     generation     : {value['generation']}")
                if "initial_translated" in value:
                    print(f"     initial_translated : {value['initial_translated']}")
                if "source" in value:
                    print(f"     source     : {value['source']}")
                if "route" in value:
                    print(f"     route      : {value['route']}")
                    
        print("\n")
        print("Generation: ", final_state.get("final_translated", final_state.get("generation", "")))
        print("="*100, "\n")
        
        # ✅ Return the final state instead of None
        return final_state
        
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")
        # ✅ Return error info
        return {"error": str(e)}


# %%
#----9. Main 실행 블록----
import uuid

#----9. Main 실행 블록----
if __name__ == "__main__":
    # 기존: 미리 정해진 입력으로 테스트
    """
    inputs = [
        ['Hello, I have a question about your religion. I hope you can answer me.', 'Can I get more info on this?']
    ]
    
    for session in inputs:
        session_id = str(uuid.uuid4())
        print(f"--- Starting New Session: {session_id} ---")
        for msg in session:
            run(msg, session_id)
        print(f"--- Finished Session: {session_id} ---\n")
    """

    # 새 버전: 콘솔에서 실시간 입력받기
    session_id = str(uuid.uuid4())
    print(f"--- Starting Interactive Session: {session_id} ---")
    print("질문을 입력해서 챗봇과 대화할 수 있습니다.")
    print("대화를 끝내려면 'exit', 'quit', 또는 'q' 를 입력하세요.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n강제 종료 요청 감지. 대화를 종료합니다.")
            break

        # 종료 명령
        if user_input.lower() in ("exit", "quit", "q"):
            print("대화를 종료합니다.")
            break

        # 빈 입력이면 무시
        if not user_input:
            continue

        # 한 턴 실행
        run(user_input, session_id)






