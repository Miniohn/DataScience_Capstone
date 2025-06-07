import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Optional, Tuple
from core.config import logger
from core.config import QnAData

# =============================================================================
# 2. RAG 시스템 구현 (목사님 Agent용)
# =============================================================================

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