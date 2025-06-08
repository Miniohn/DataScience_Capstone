import openai
import logging
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
            # OpenAI Moderation API 사용
            moderation_response = openai.Moderation.create(input=user_input)
            is_flagged = moderation_response.results[0].flagged
            
            if is_flagged:
                categories = moderation_response.results[0].categories
                flagged_categories = [cat for cat, flagged in categories.items() if flagged]
                return self._generate_warning_message(flagged_categories)
            
            # 추가적인 커스텀 검사
            if self._custom_inappropriate_check(user_input):
                return self._generate_custom_warning()
            
            return None  # 적절한 내용인 경우 None 반환
            
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
                "Please share what's truly on your heart.")