# =============================================================================
# 7. WhatsApp 전용 알림 시스템
# =============================================================================

class WhatsAppNotificationManager:
    def __init__(self):
        """WhatsApp 전용 알림 관리자 초기화"""
        self.counselors = self._load_counselors()
        self.whatsapp_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    
    def _load_counselors(self) -> Dict[str, Counselor]:
        """상담사 정보 로드 (WhatsApp만)"""
        return {
            "pastor_john": Counselor(
                id="pastor_john",
                name="Pastor John",
                whatsapp=os.getenv("PASTOR_JOHN_WHATSAPP", "+1234567890"),
                expertise=["pastoral_care", "spiritual_guidance", "biblical_interpretation", "theology"],
                availability="9AM-9PM",
                priority=1
            ),
            "missionary_sarah": Counselor(
                id="missionary_sarah",
                name="Missionary Sarah",
                whatsapp=os.getenv("MISSIONARY_SARAH_WHATSAPP", "+1234567891"),
                expertise=["cross_cultural", "missions", "spiritual_guidance", "discipleship"],
                availability="24/7",
                priority=1
            ),
            "counselor_mary": Counselor(
                id="counselor_mary",
                name="Counselor Mary",
                whatsapp=os.getenv("COUNSELOR_MARY_WHATSAPP", "+1234567892"),
                expertise=["depression", "anxiety", "trauma", "grief", "general_counseling"],
                availability="9AM-6PM",
                priority=2
            )
        }
    
    def send_handoff_notifications(self, handoff_request: HandoffRequest):
        """WhatsApp으로만 핸드오프 알림 전송"""
        try:
            # 적절한 상담사들 선택
            target_counselors = self._select_counselors(
                handoff_request.urgency, 
                handoff_request.counselor_type
            )
            
            for counselor in target_counselors:
                # WhatsApp 알림만 전송
                self._send_whatsapp_notification(counselor, handoff_request)
            
            logger.info(f"WhatsApp notifications sent for {handoff_request.user_phone}")
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp notifications: {e}")
    
    def _select_counselors(self, urgency: HandoffUrgency, counselor_type: str) -> List[Counselor]:
        """적절한 상담사들 선택"""
        selected = []
        
        # Pastor Agent에서 온 요청이면 선교사/목사님 우선
        if counselor_type in ["pastor", "missionary"]:
            pastoral_counselors = [c for c in self.counselors.values() 
                                 if "pastoral_care" in c.expertise or "spiritual_guidance" in c.expertise]
            selected.extend(pastoral_counselors)
        
        # 일반 상담의 경우
        elif counselor_type == "counselor":
            general_counselors = [c for c in self.counselors.values() 
                                if "general_counseling" in c.expertise]
            selected.extend(general_counselors)
        
        # 우선순위 정렬
        selected.sort(key=lambda x: x.priority)
        
        return selected[:2]  # 최대 2명
    
    def _send_whatsapp_notification(self, counselor: Counselor, handoff_request: HandoffRequest):
        """WhatsApp 알림 전송"""
        urgency_emoji = {
            HandoffUrgency.HIGH: "🙏",      # 깊은 영적 질문
            HandoffUrgency.MEDIUM: "📋",    # 일반 상담
            HandoffUrgency.LOW: "💬"        # 간단한 질문
        }
        
        message = f"""
{urgency_emoji.get(handoff_request.urgency, '📋')} PASTORAL GUIDANCE NEEDED

Level: {handoff_request.urgency.value}
Counselor: {counselor.name}
Reason: {handoff_request.reason}
User: {handoff_request.user_phone}
Time: {handoff_request.timestamp}

User's Question:
"{handoff_request.user_message}"

This question seems beyond AI's capability and would benefit from your pastoral wisdom.

Reply 'ACCEPT {handoff_request.session_id}' to take this case.
Reply 'INFO {handoff_request.session_id}' for full conversation.
Reply 'BUSY' if you're currently unavailable.
        """
        
        # WhatsApp Business API 호출
        success = self._send_whatsapp_message(counselor.whatsapp, message)
        
        if success:
            logger.info(f"Notification sent to {counselor.name} via WhatsApp")
        else:
            logger.error(f"Failed to send notification to {counselor.name}")
    
    def _send_whatsapp_message(self, to_phone: str, message: str) -> bool:
        """WhatsApp 메시지 전송"""
        try:
            if not self.whatsapp_token or not self.phone_number_id:
                logger.warning("WhatsApp credentials not configured")
                return False
            
            url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to_phone,
                "type": "text",
                "text": {"body": message}
            }
            
            headers = {
                "Authorization": f"Bearer {self.whatsapp_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                logger.info(f"WhatsApp message sent to {to_phone}")
                return True
            else:
                logger.error(f"Failed to send WhatsApp message: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return False
    
    def send_user_notification(self, user_phone: str, message: str):
        """사용자에게 WhatsApp 메시지 전송"""
        return self._send_whatsapp_message(user_phone, message)
