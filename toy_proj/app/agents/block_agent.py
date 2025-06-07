import requests
import openai
import logging
from collections import defaultdict

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BlockAgent:
    def __init__(self):
        self.system_prompt = """
        You are a content moderation agent for a Christian counseling service.
        
        Your role is to detect inappropriate content including:
        - Profanity and offensive language
        - Spam or promotional content
        - Harmful or threatening messages
        - Sexually explicit content
        - Content that promotes violence or illegal activities
        
        Additionally, you need to detect off-topic content like:
        - Requests for business transactions, visa questions, or unrelated queries
        
        When you detect such content, respond with a polite but firm warning message in English.
        If the content is borderline but not clearly inappropriate, give the user the benefit of the doubt
        and provide a gentle reminder about maintaining respectful communication.
        
        After three warnings, you need to end the conversation and stop responding to the user.
        """
        
        # 경고 횟수 추적 (사용자별)
        self.user_warning_count = defaultdict(int)
    
    def process(self, user_input: str, user_phone: str) -> str:
        """부적절한 콘텐츠 분석 및 경고 메시지 생성"""
        try:
            # OpenAI Moderation API 사용하여 메시지 필터링
            moderation_response = openai.Moderation.create(input=user_input)
            is_flagged = moderation_response.results[0].flagged
            flagged_categories = self._get_flagged_categories(moderation_response)

            if is_flagged or self._is_off_topic(user_input):
                # 경고 메시지 생성
                warning_message = self._generate_warning_message(flagged_categories, user_input)
                self.user_warning_count[user_phone] += 1

                # 경고 3회 이상 시 대화 종료
                if self.user_warning_count[user_phone] >= 3:
                    self._end_conversation(user_phone)
                    return "You have been warned multiple times. The conversation has been ended."

                return warning_message
            
            return None  # 부적절하지 않으면 None 반환 (다른 에이전트로 라우팅됨)

        except Exception as e:
            logger.error(f"Error in block agent processing: {e}")
            return "I apologize, but I am experiencing issues with processing your message."

    def _get_flagged_categories(self, moderation_response) -> list:
        """모더레이션 결과에서 플래그된 카테고리 추출"""
        categories = moderation_response.results[0].categories
        flagged_categories = [cat for cat, flagged in categories.items() if flagged]
        return flagged_categories
    
    def _is_off_topic(self, text: str) -> bool:
        """주제와 관련 없는 대화 필터링 (예: 비자 관련 질문)"""
        off_topic_keywords = ['visa', 'job', 'money', 'buy', 'free', 'sell', 'business', 'visa application']
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in off_topic_keywords)
    
    def _generate_warning_message(self, flagged_categories: list, user_input: str) -> str:
        """카테고리별 경고 메시지 생성"""
        base_message = (
            "I understand you may be going through a difficult time, "
            "but I need to ask that we keep our conversation respectful and appropriate. "
        )
        
        if 'harassment' in flagged_categories:
            return base_message + "Please avoid using threatening or harassing language."
        elif 'hate' in flagged_categories:
            return base_message + "Let's focus on positive and loving communication."
        elif 'sexual' in flagged_categories:
            return base_message + "Please keep our conversation focused on counseling and spiritual matters."
        elif self._is_off_topic(user_input):
            return base_message + "This is a space for spiritual counseling. Let's keep our conversation related to faith and guidance."
        else:
            return base_message + "Please rephrase your message in a more appropriate way."
    
    def _end_conversation(self, user_phone: str):
        """사용자 대화 종료"""
        logger.info(f"Ending conversation with user {user_phone} due to repeated violations.")
        
        try:
            # 사용자가 계속해서 부적절한 대화를 할 경우, 대화 종료 처리
            self._send_whatsapp_end_message(user_phone)
            logger.info(f"Conversation with {user_phone} has been ended.")
        
        except Exception as e:
            logger.error(f"Error while ending conversation with user {user_phone}: {e}")
    
    def _send_whatsapp_end_message(self, user_phone: str):
        """WhatsApp API를 통해 대화 종료 메시지 전송"""
        url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": user_phone,
            "type": "text",
            "text": {
                "body": "You have been warned multiple times for inappropriate content. The conversation has been ended."
            }
        }
        
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"End message sent to {user_phone}")
        else:
            logger.error(f"Failed to send end message to {user_phone}. Response: {response.text}")
