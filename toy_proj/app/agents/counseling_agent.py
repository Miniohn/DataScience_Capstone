import openai
import logging
from app.models import AgentType

logger = logging.getLogger(__name__)

class CounselingAgent:
    """상담 Agent (일반 상담)"""
    def __init__(self):
        self.system_prompt = """
        You are a Christian counselor born and raised in a conservative Christian family.
        You are currently engaged in missionary work for Muslim communities.

        Your characteristics:
        - Deep understanding of challenges faced by Muslim individuals
        - Speak with the love and compassion of Jesus Christ
        - Provide gentle, empathetic counseling
        - Bridge cultural and religious understanding with sensitivity
        - Always respond in English as the default language
        - Respect diverse backgrounds while sharing Christian love

        When counseling:
        1. Listen with empathy and understanding
        2. Provide biblical wisdom with cultural sensitivity
        3. Offer hope and encouragement rooted in Christ's love
        4. Respect the person's background and current struggles
        5. Never be pushy about faith but let love speak through your words
        6. Focus on healing, hope, and God's unconditional love
        """
        
        self.conversation_history = []
    
    def process(self, user_input: str, session_id: str = "default") -> str:
        """상담 응답 생성"""
        try:
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # 대화 히스토리가 너무 길어지면 최근 메시지만 유지
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-8:]
            
            messages = [{"role": "system", "content": self.system_prompt}] + self.conversation_history
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            assistant_response = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": assistant_response})
            
            return assistant_response
            
        except Exception as e:
            logger.error(f"Error in counseling agent processing: {e}")
            return ("I'm here to listen and support you. Please tell me more about what you're "
                   "going through, and I'll do my best to help you find peace and guidance.")
    
    def reset_conversation(self, session_id: str = "default"):
        """대화 히스토리 초기화"""
        self.conversation_history = []