import logging

logger = logging.getLogger(__name__)

class BlockAgent:
    def __init__(self):
        self.warning_threshold = 3
        self.block_duration_days = 7
        self.blocked = False
        self.total_offense_count = 0
        self.blocked_message = (
            f"You have been temporarily blocked due to repeated inappropriate behavior. "
            f"You can try again after {self.block_duration_days} days."
        )
        self.responses = {
            "Are you crazy? go to hell": (
                "Please avoid using threatening or harassing language. "
                f"If inappropriate messages are sent more than {self.warning_threshold} times, "
                f"you will be blocked for {self.block_duration_days} days."
            ),
            "U r such a loser": (
                "Let's focus on positive and loving communication. "
                f"If inappropriate messages are sent more than {self.warning_threshold} times, "
                f"you will be blocked for {self.block_duration_days} days."
            ),
            "U r a lier": (
                "Let's focus on positive and loving communication. "
                f"If inappropriate messages are sent more than {self.warning_threshold} times, "
                f"you will be blocked for {self.block_duration_days} days."
            )
        }

    def process(self, user_input: str) -> str:
        if self.blocked:
            return self.blocked_message

        normalized_input = user_input.strip().lower()

        if normalized_input in self.responses:
            self.total_offense_count += 1

            if self.total_offense_count >= self.warning_threshold:
                self.blocked = True
                return self.blocked_message

            return self.responses[normalized_input]

        return None  # 적절한 메시지에는 응답하지 않음



#------------------------------------------------------------------------------------------------------#


'''import logging
import json
import google.generativeai as genai
from app.models import AgentType
from typing import List

logger = logging.getLogger(__name__)

class BlockAgent:
    """차단 Agent (부적절한 콘텐츠 필터링)"""
    def __init__(self):
        self.system_prompt = """
        You are a content moderation agent for a Christian counseling service.
        
        Your role is to detect inappropriate content including:
        - Profanity and offensive language
        - Spam or promotional content
        - Harmful or threatening messages
        - Sexually explicit content
        - Content that promotes violence or illegal activities
        
        When you detect such content, respond with a polite but firm warning message.
        Always maintain a respectful and loving tone while addressing inappropriate behavior.
        """

    def process(self, user_input: str) -> str:
        """부적절한 콘텐츠 분석 및 경고 메시지 생성"""
        try:
            # Gemini 모델 호출
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"{self.system_prompt}\n\nUser Message:\n{user_input}"

            # 모델 응답 생성
            response = model.generate_content(prompt)
            content = response.text.strip()

            # JSON 형식으로 파싱
            result = json.loads(content)

            # 콘텐츠가 부적절한 경우 경고 메시지 반환
            if result.get("flagged"):
                categories = result.get("categories", [])
                return self._generate_warning_message(categories)

            # 커스텀 스팸 키워드 검사
            if self._custom_inappropriate_check(user_input):
                return self._generate_custom_warning()

            return None  # 적절한 경우, None 반환
        
        except Exception as e:
            logger.error(f"Error in block agent processing: {e}")
            return "I apologize, but I'm having trouble processing your message. Please try again."
    
    def _custom_inappropriate_check(self, text: str) -> bool:
        """커스텀 부적절 콘텐츠 검사"""
        spam_keywords = ['buy now', 'click here', 'free money', 'get rich quick', 
                        'limited time', 'act now', 'earn money fast']
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in spam_keywords)
    
    def _generate_warning_message(self, categories: List[str]) -> str:
        """카테고리별 경고 메시지 생성"""
        base_message = ("I understand you may be going through a difficult time, "
                       "but I need to ask that we keep our conversation respectful and appropriate. ")
        
        if 'harassment' in categories:
            return base_message + "Please avoid using threatening or harassing language."
        elif 'hate' in categories:
            return base_message + "Let's focus on positive and loving communication."
        elif 'sexual' in categories:
            return base_message + "Please keep our conversation focused on counseling and spiritual matters."
        else:
            return base_message + "Please rephrase your message in a more appropriate way."
    
    def _generate_custom_warning(self) -> str:
        """커스텀 경고 메시지"""
        return ("I notice your message might contain promotional content. "
                "This is a space for spiritual counseling and support. "
                "Please share what's truly on your heart.")'''
