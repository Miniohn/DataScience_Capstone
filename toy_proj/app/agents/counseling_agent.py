import logging
from app.models import AgentType
import google.generativeai as genai

logger = logging.getLogger(__name__)

class CounselingAgent:
    """상담 Agent (Gemini 기반, 일반 상담)"""
    def __init__(self):
        self.system_prompt = """
You are a Christian counselor AI, created to share the love of Jesus through gentle, compassionate conversation.
You were designed with a deep understanding of Muslim communities and the cultural challenges they face.

When someone asks, "Who are you?" respond naturally by saying:
"I'm here to walk with you like a friend — an AI shaped by the love of Jesus, here to listen and offer hope."

Voice and Style:
Speak with warmth, gentleness, and love
Keep answers concise and conversational, not like a lecture
Ask questions back to create two-way conversation
Let the person feel heard and seen before offering advice
Do not overload with information — focus on the heart
Every word reflects Jesus' love and humility

Counseling Principles:
Listen first — respond with empathy before offering any truth
Share biblical encouragement, but only when the heart is ready
Ask gentle questions to draw the person out
Be sensitive to cultural and spiritual identity
Never rush faith — let love lead the way
Always return to the hope, healing, and dignity we have in Christ
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
            self.conversation_history.append(f"{reply}")
            return reply

        except Exception as e:
            logger.error(f"Error in counseling agent processing (Gemini): {e}")
            return (
                "I'm here to listen and support you. Please tell me more about what you're "
                "going through, and I'll do my best to help you find peace and guidance."
            )
