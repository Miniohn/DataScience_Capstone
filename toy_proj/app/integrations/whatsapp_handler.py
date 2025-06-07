# whatsapp 웹훅 핸들러
import os
import logging
from app.chatbot_system import ChatbotSystem # 순환 참조 주의! (나중에 수정)
from typing import Dict, List

logger = logging.getLogger(__name__)

class WhatsAppHandler:
    def __init__(self, chatbot_system: ChatbotSystem):
        self.chatbot = chatbot_system
        self.verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN")
    
    def handle_incoming_message(self, webhook_data: dict) -> dict:
        """WhatsApp 메시지 처리"""
        try:
            # 메시지 추출
            entry = webhook_data.get('entry', [])
            if not entry:
                return {"status": "no_entry"}
            
            changes = entry[0].get('changes', [])
            if not changes:
                return {"status": "no_changes"}
            
            value = changes[0].get('value', {})
            messages = value.get('messages', [])
            
            if not messages:
                return {"status": "no_messages"}
            
            message = messages[0]
            from_phone = message.get('from')
            message_text = message.get('text', {}).get('body', '')
            
            if not message_text:
                return {"status": "empty_message"}
            
            # 챗봇으로 메시지 처리
            result = self.chatbot.process_message(message_text, from_phone)
            
            # 사용자에게 응답 전송
            self._send_response(from_phone, result['response'])
            
            return {"status": "processed", "result": result}
            
        except Exception as e:
            logger.error(f"Error handling WhatsApp message: {e}")
            return {"status": "error", "message": str(e)}
    
    def handle_counselor_response(self, webhook_data: dict) -> dict:
        """상담사 응답 처리"""
        try:
            message_text = self._extract_message_text(webhook_data)
            from_phone = self._extract_from_phone(webhook_data)
            
            if message_text.upper().startswith('ACCEPT'):
                session_id = message_text.split()[1] if len(message_text.split()) > 1 else None
                if session_id and session_id in self.chatbot.active_handoffs:
                    # 핸드오프 수락 처리
                    handoff_request = self.chatbot.active_handoffs[session_id]
                    
                    # 사용자에게 알림
                    user_message = f"Great news! A counselor is now available to speak with you personally. They will be in touch shortly to provide more detailed guidance for your situation."
                    self._send_response(handoff_request.user_phone, user_message)
                    
                    # 상담사에게 확인
                    counselor_message = f"You have successfully accepted the counseling case for {session_id}. The user has been notified."
                    self._send_response(from_phone, counselor_message)
                    
                    # 활성 핸드오프에서 제거
                    del self.chatbot.active_handoffs[session_id]
                    
                    return {"status": "accepted", "session_id": session_id}
            
            elif message_text.upper().startswith('INFO'):
                session_id = message_text.split()[1] if len(message_text.split()) > 1 else None
                if session_id:
                    # 대화 히스토리 전송
                    history = self.chatbot.get_session_history(session_id)
                    history_text = self._format_conversation_history(history)
                    self._send_response(from_phone, f"Conversation History for {session_id}:\n\n{history_text}")
                    
                    return {"status": "info_sent", "session_id": session_id}
            
            elif message_text.upper() == 'BUSY':
                # 다른 상담사에게 재라우팅 로직
                busy_message = "Understood. We'll route urgent cases to other available counselors."
                self._send_response(from_phone, busy_message)
                
                return {"status": "marked_busy"}
            
            return {"status": "unknown_command"}
            
        except Exception as e:
            logger.error(f"Error handling counselor response: {e}")
            return {"status": "error", "message": str(e)}
    
    def _extract_message_text(self, webhook_data: dict) -> str:
        """웹훅 데이터에서 메시지 텍스트 추출"""
        try:
            entry = webhook_data.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            messages = value.get('messages', [{}])
            return messages[0].get('text', {}).get('body', '')
        except:
            return ""
    
    def _extract_from_phone(self, webhook_data: dict) -> str:
        """웹훅 데이터에서 발신자 전화번호 추출"""
        try:
            entry = webhook_data.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            messages = value.get('messages', [{}])
            return messages[0].get('from', '')
        except:
            return ""
    
    def _send_response(self, to_phone: str, message: str):
        """WhatsApp으로 응답 전송"""
        return self.chatbot.notification_manager._send_whatsapp_message(to_phone, message)
    
    def _format_conversation_history(self, history: List[Dict]) -> str:
        """대화 히스토리 포맷팅"""
        formatted = []
        for i, entry in enumerate(history, 1):
            formatted.append(f"{i}. User: {entry.get('user_input', '')}")
            formatted.append(f"   AI ({entry.get('agent_type', '')}): {entry.get('response', '')[:100]}...")
            formatted.append("")
        
        return "\n".join(formatted)