# =============================================================================
# 8. Handoff Judge Agent (핸드오프 판단 Agent)
# =============================================================================

class HandoffJudgeAgent:
    def __init__(self):
        self.system_prompt = """
        You are an expert counseling supervisor who decides when AI should transfer 
        conversations to human missionaries/pastors.
        
        Focus specifically on Pastor Agent conversations - when AI limitations are reached.
        
        DECISION CRITERIA for Pastor Agent:
        1. THEOLOGICAL COMPLEXITY (HIGH): 
           - Deep doctrinal questions requiring seminary-level knowledge
           - Complex biblical interpretation beyond basic verses
           - Questions about church history, systematic theology
           - Denominational differences, controversial theological topics
           - Questions requiring pastoral wisdom and experience
        
        2. PASTORAL WISDOM NEEDED (MEDIUM):
           - Life decisions requiring spiritual discernment  
           - Ministry calling and vocation questions
           - Spiritual disciplines and growth beyond basics
           - Grief counseling with theological depth
        
        3. AI CAN HANDLE (LOW):
           - Basic biblical questions with clear answers
           - Simple prayer requests
           - General encouragement from Scripture
           - Common Christian living questions
        
        For Counseling Agent - only consider handoff for persistent issues needing ongoing support.
        
        Respond ONLY in JSON:
        {
            "handoff_needed": true/false,
            "urgency_level": "LOW/MEDIUM/HIGH", 
            "primary_reason": "specific reason why AI cannot adequately address this",
            "confidence_score": 0.85,
            "counselor_type": "pastor/missionary/counselor",
            "transition_message": "gentle message explaining why human guidance would be better"
        }
        """
        
        self.conversation_history = []
    
    def evaluate_handoff(self, current_message: str, agent_response: str, 
                        conversation_context: list, agent_type: str) -> dict:
        """현재 대화 상황을 분석하여 핸드오프 필요성 판단"""
        try:
            # 대화 히스토리 구성
            context_summary = self._build_context_summary(conversation_context, 
                                                         current_message, 
                                                         agent_response, 
                                                         agent_type)
            
            # AI 판단 요청
            judgment_prompt = f"""
            CONVERSATION ANALYSIS REQUEST:
            
            Current Context:
            - Agent Type: {agent_type}
            - User Message: "{current_message}"
            - AI Response: "{agent_response}"
            
            Conversation Summary:
            {context_summary}
            
            Based on this conversation, should we transfer to a human counselor?
            Consider the depth of spiritual questions, emotional intensity, 
            and whether AI responses are meeting the user's needs.
            
            Provide your assessment in the required JSON format.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": judgment_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            judgment = json.loads(response.choices[0].message.content)
            
            # 결과 검증 및 기본값 설정
            return self._validate_judgment(judgment)
            
        except Exception as e:
            logger.error(f"Error in handoff evaluation: {e}")
            return self._get_default_judgment()
    
    def _build_context_summary(self, conversation_context: list, 
                              current_message: str, agent_response: str, 
                              agent_type: str) -> str:
        """대화 컨텍스트 요약 생성"""
        if not conversation_context:
            return f"First interaction - User: {current_message}"
        
        # 최근 3-5턴의 대화만 요약
        recent_context = conversation_context[-5:] if len(conversation_context) > 5 else conversation_context
        
        summary_parts = []
        summary_parts.append(f"Conversation Length: {len(conversation_context)} turns")
        summary_parts.append(f"Current Agent: {agent_type}")
        summary_parts.append("\nRecent Conversation:")
        
        for entry in recent_context:
            summary_parts.append(f"User: {entry.get('user_input', '')}")
            summary_parts.append(f"AI ({entry.get('agent_type', 'unknown')}): {entry.get('response', '')[:200]}...")
        
        summary_parts.append(f"\nCurrent Exchange:")
        summary_parts.append(f"User: {current_message}")
        summary_parts.append(f"AI ({agent_type}): {agent_response}")
        
        return "\n".join(summary_parts)
    
    def _validate_judgment(self, judgment: dict) -> dict:
        """판단 결과 검증 및 정규화"""
        validated = {
            "handoff_needed": judgment.get("handoff_needed", False),
            "urgency_level": judgment.get("urgency_level", "LOW"),
            "primary_reason": judgment.get("primary_reason", "No specific reason provided"),
            "confidence_score": min(1.0, max(0.0, judgment.get("confidence_score", 0.5))),
            "counselor_type": judgment.get("counselor_type", "counselor"),
            "user_readiness": judgment.get("user_readiness", "medium"),
            "transition_message": judgment.get("transition_message", "")
        }
        
        # 긴급 상황 체크
        if validated["urgency_level"] == "CRITICAL":
            validated["handoff_needed"] = True
            validated["user_readiness"] = "high"
        
        return validated
    
    def _get_default_judgment(self) -> dict:
        """에러 발생 시 기본 판단"""
        return {
            "handoff_needed": False,
            "urgency_level": "LOW",
            "primary_reason": "System error - continuing with AI",
            "confidence_score": 0.3,
            "counselor_type": "counselor",
            "user_readiness": "low",
            "transition_message": ""
        }
    
    def generate_handoff_message(self, judgment: dict) -> str:
        """핸드오프 제안 메시지 생성"""
        if not judgment["handoff_needed"]:
            return ""
        
        urgency = judgment["urgency_level"]
        counselor_type = judgment["counselor_type"]
        
        if urgency == "CRITICAL":
            return ("I'm concerned about what you're going through right now. "
                   "Let me connect you immediately with a crisis counselor who "
                   "can provide the immediate support you need. Please stay with me.")
        
        elif urgency == "HIGH":
            return (f"I can see you're dealing with some deep and important questions. "
                   f"I'd like to connect you with {self._get_counselor_description(counselor_type)} "
                   f"who can provide more personalized guidance. Would that be helpful?")
        
        elif urgency == "MEDIUM":
            return (f"Your questions touch on some profound spiritual matters. "
                   f"While I'm here to support you, you might benefit from speaking "
                   f"with {self._get_counselor_description(counselor_type)} who can offer "
                   f"deeper, ongoing guidance. Would you be interested in that option?")
        
        else:  # LOW
            return (f"If you'd ever like to speak with a human counselor for more "
                   f"personalized support, I can arrange that. For now, I'm happy "
                   f"to continue our conversation.")
    
    def _get_counselor_description(self, counselor_type: str) -> str:
        """상담사 타입별 설명"""
        descriptions = {
            "pastor": "one of our experienced pastors",
            "counselor": "a professional Christian counselor", 
            "crisis_specialist": "a crisis intervention specialist",
            "chaplain": "a chaplain"
        }
        return descriptions.get(counselor_type, "a professional counselor")