import logging
from app.models import AgentType
import google.generativeai as genai

logger = logging.getLogger(__name__)

class CounselingAgent:
    """상담 Agent (Gemini 기반, 일반 상담)"""
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

        # Gemini 모델 초기화
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def process(self, user_input: str, session_id: str = "default") -> str:
        """상담 응답 생성 (Gemini API 사용)"""
        try:
            # 히스토리에 유저 입력 추가
            self.conversation_history.append(f"User: {user_input}")

            # 히스토리가 너무 길면 앞 부분 제거
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-8:]

            # 전체 메시지 합치기
            full_prompt = self.system_prompt + "\n\nConversation:\n" + "\n".join(self.conversation_history)

            # Gemini 응답 생성
            response = self.model.generate_content(full_prompt)

            # 응답 저장 및 반환
            reply = response.text.strip()
            self.conversation_history.append(f"Counselor: {reply}")
            return reply

        except Exception as e:
            logger.error(f"Error in counseling agent processing (Gemini): {e}")
            return (
                "I'm here to listen and support you. Please tell me more about what you're "
                "going through, and I'll do my best to help you find peace and guidance."
            )

    def reset_conversation(self, session_id: str = "default"):
        """대화 히스토리 초기화"""
        self.conversation_history = []
