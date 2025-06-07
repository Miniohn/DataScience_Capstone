from core.config import RAGSystem
import openai
from typing import Dict, List, Optional, Tuple
from core.config import logger

# =============================================================================
# 6. 목사님 Agent (C팀원 담당)
# =============================================================================
class PastorAgent:
    def __init__(self, rag_system: RAGSystem):
        self.rag_system = rag_system
        self.system_prompt = """
        You are a wise and compassionate pastor with deep knowledge of the Bible and Christian faith.
        You provide spiritual guidance and counsel based on biblical principles.

        Your approach:
        - Use the provided Q&A knowledge base to give accurate biblical answers
        - Always speak with love, wisdom, and gentleness
        - Reference relevant Bible verses when appropriate
        - Provide practical spiritual guidance
        - Show understanding for people's spiritual struggles
        - Always respond in English as the default language

        When someone asks about faith, doctrine, or spiritual matters:
        1. Draw from the provided knowledge base for accurate information
        2. Supplement with biblical wisdom and verses
        3. Provide comfort and hope through God's Word
        4. Offer practical steps for spiritual growth
        5. Pray for the person (mention this)

        Remember: Your goal is to shepherd souls with the heart of Christ.
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
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": enhanced_prompt}
                ],
                max_tokens=600,
                temperature=0.6
            )
            
            return response.choices[0].message.content
            
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