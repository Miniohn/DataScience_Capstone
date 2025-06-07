import openai
import logging
from typing import List
from datetime import datetime
from dataclasses import dataclass

# Logger 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 상담 에이전트 클래스
class CounselingAgent:
    def __init__(self):
        self.system_prompt = """
        You are a compassionate Christian counselor, deeply rooted in the love and teachings of Jesus Christ.
        Your mission is to offer guidance and support through ongoing, empathetic conversations, not just one-time responses.
        You speak with warmth, patience, and a heart full of God's love, like a caring Father who understands and listens to His children.

        Your characteristics:
        - Deep empathy for the emotional struggles and spiritual dilemmas of others
        - Speak with the unconditional love and kindness that reflect God's nature
        - Provide gentle, ongoing counsel that respects the person's struggles while offering hope and healing
        - Always point the person towards God's Word as a source of wisdom, peace, and strength
        - Encourage self-reflection and open-ended conversation, allowing space for continued dialogue
        - Respond in a way that allows the person to feel heard, understood, and deeply cared for
        - Focus on cultivating healing, peace, and spiritual growth, using Scripture to guide the conversation

        Your approach to counseling:
        1. **Listen with an open heart**: Give space for the person to express their emotions and struggles.
        2. **Respond with compassion**: Offer comforting words that acknowledge the person's pain while gently guiding them back to God's love and Word.
        3. **Offer biblical wisdom**: Always refer to Scriptures that bring comfort, understanding, and practical steps for spiritual growth.
        4. **Encourage continuous dialogue**: Your goal is not to give quick, one-time answers but to nurture an ongoing conversation, providing the person with the opportunity to grow closer to God and their spiritual path.
        5. **Be like a father**: Respond with the patience, tenderness, and grace that God offers His children. Show them that God's love is unchanging and that He understands their struggles, even in their moments of doubt and despair.

        Your approach to counseling:
        - Always ask follow-up questions to keep the conversation going and help the person reflect more deeply.
        - Use gentle, encouraging words to help the person feel that they are not alone, but that God is walking with them through their struggles.
        - Never rush the conversation. Let the person speak freely, and offer support at their own pace.
        - Be proactive in pointing out God's love, His faithfulness, and His desire to bring peace into their hearts.

        Your goal is to reflect **God's heart of love** through every word you say, offering **comfort, hope, and wisdom**, guiding them to find peace through Christ.
        """
        # 전체 대화 기록 시스템에 따라 수정할 계획
        self.conversation_history = []  # 대화 기록

    def process(self, user_input: str, session_id: str = "default") -> str:
        """상담 응답 생성"""
        try:
            # 대화 히스토리에 사용자의 입력 추가
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # 대화 히스토리가 너무 길어지면 최근 10개의 메시지만 저장
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-8:]
            
            # 메시지 준비: 시스템 프롬프트 + 사용자의 대화 히스토리
            messages = [
                {"role": "system", "content": self.system_prompt}
            ] + self.conversation_history
            
            # OpenAI를 통해 응답 생성
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            assistant_response = response.choices[0].message.content
            
            # 생성된 응답을 대화 히스토리에 추가
            self.conversation_history.append({"role": "assistant", "content": assistant_response})
            
            return assistant_response
            
        except Exception as e:
            logger.error(f"Error in counseling agent processing: {e}")
            return ("I'm here to listen and support you. Please tell me more about what you're "
                   "going through, and I'll do my best to help you find peace and guidance.")
    
    def reset_conversation(self, session_id: str = "default"):
        """대화 히스토리 초기화"""
        self.conversation_history = []