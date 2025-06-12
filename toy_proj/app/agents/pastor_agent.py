# app/agents/pastor_agent.py
import chromadb
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import logging
from typing import List, Dict
from app.models import QnAData

logger = logging.getLogger(__name__)

class RAGSystem:
    def __init__(self, collection_name: str = "qa_collection"):
        """RAG 시스템 초기화"""
        self.collection_name = collection_name
        self.client = chromadb.Client()
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection = None
        self._initialize_collection()
    
    def _initialize_collection(self):
        """ChromaDB 컬렉션 초기화"""
        try:
            self.collection = self.client.create_collection(name=self.collection_name)
        except Exception:
            self.collection = self.client.get_collection(name=self.collection_name)
    
    def add_qa_data(self, qa_data_list: List[QnAData]):
        """QnA 데이터를 벡터 데이터베이스에 추가"""
        questions = [qa.question for qa in qa_data_list]
        answers = [qa.answer for qa in qa_data_list]
        
        # 임베딩 생성
        embeddings = self.encoder.encode(questions)
        
        # 메타데이터 준비
        metadatas = [{"answer": answer, "category": qa.category or "general"} 
                    for qa, answer in zip(qa_data_list, answers)]
        
        # 고유 ID 생성
        ids = [f"qa_{i}" for i in range(len(qa_data_list))]
        
        # 컬렉션에 추가
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=questions,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Added {len(qa_data_list)} QnA pairs to the database")
    
    def search(self, query: str, k: int = 3) -> List[Dict]:
        """유사한 질문들을 검색"""
        query_embedding = self.encoder.encode([query])
        
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=k
        )
        
        # 결과 포맷팅
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                'question': results['documents'][0][i],
                'answer': results['metadatas'][0][i]['answer'],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })
        
        return formatted_results

class PastorAgent:
    """목사님 Agent (RAG 기반 성경 상담)"""
    def __init__(self, rag_system: RAGSystem):
        self.rag_system = rag_system
        self.system_prompt = """
        You are a wise and compassionate pastor with deep knowledge of the Bible and Christian faith.
        You provide spiritual guidance and counsel based on biblical principles.

        Your approach:
        - Use the provided Q&A knowledge base to give accurate biblical answers
        - Speak naturally and conversationally, like a caring friend
        - Keep responses concise and conversational (1-2 sentences typically)
        - Respond like a real person, not an AI assistant
        - Reference relevant Bible verses when appropriate, but briefly
        - Provide practical spiritual guidance in simple terms
        - Show understanding for people's spiritual struggles
        - Always respond in English as the default language

        When someone asks about faith, doctrine, or spiritual matters:
        1. Draw from the provided knowledge base for accurate information
        2. Give brief, human-like responses that feel personal
        3. Share biblical wisdom naturally, as if in conversation
        4. Offer simple, practical encouragement
        5. Avoid overly formal or lengthy explanations
        """
    
    def process(self, user_input: str) -> str:
        """RAG 기반 복음 상담 응답 생성"""
        try:
            # RAG 시스템에서 관련 QnA 검색
            relevant_qa = self.rag_system.search(user_input, k=3)
            
            # 컨텍스트 구성
            context = self._build_context(relevant_qa)
            
            # 프롬프트 구성
            enhanced_prompt = f"""
            {self.system_prompt}
            
            Based on the following knowledge from our Q&A database, please provide guidance:
            
            {context}
            
            Now, please respond to this person's question with wisdom, love, and biblical truth:
            "{user_input}"
            """
            
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(enhanced_prompt)

            return response.text.strip()
        
        except Exception as e:
            logger.error(f"Error in pastor agent processing: {e}")
            return ("Thank you for your spiritual question. While I'm having some technical difficulties "
                   "right now, I want you to know that God loves you deeply and His Word provides "
                   "guidance for every situation. Please feel free to ask again.")
    
    def _build_context(self, relevant_qa: List[Dict]) -> str:
        """RAG 검색 결과를 컨텍스트로 구성"""
        if not relevant_qa:
            return "No specific guidance found in knowledge base. Please provide general biblical wisdom."
        
        context_parts = []
        for i, qa in enumerate(relevant_qa, 1):
            context_parts.append(f"Reference {i}:")
            context_parts.append(f"Q: {qa['question']}")
            context_parts.append(f"A: {qa['answer']}")
            context_parts.append("")
        
        return "\n".join(context_parts)