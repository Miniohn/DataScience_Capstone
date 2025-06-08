import logging
import json
import google.generativeai as genai
from app.models import AgentType

logger = logging.getLogger(__name__)

class HandoffJudgeAgent:
    """핸드오프 판단 Agent"""
    def __init__(self):
        self.system_prompt = """
        You are an expert counseling supervisor who decides when AI should transfer 
        conversations to human missionaries/pastors.
        
        DECISION CRITERIA:
        1. THEOLOGICAL COMPLEXITY (HIGH): 
           - Deep doctrinal questions requiring seminary-level knowledge
           - Complex biblical interpretation beyond basic verses
           - Questions about church history, systematic theology
        
        2. PASTORAL WISDOM NEEDED (MEDIUM):
           - Life decisions requiring spiritual discernment  
           - Ministry calling and vocation questions
           - Spiritual disciplines and growth beyond basics
        
        3. AI CAN HANDLE (LOW):
           - Basic biblical questions with clear answers
           - Simple prayer requests
           - General encouragement from Scripture
        
        Respond ONLY in JSON. For example:
        {
            "handoff_needed": true/false,
            "urgency_level": "LOW/MEDIUM/HIGH", 
            "primary_reason": "specific reason why AI cannot adequately address this",
            "confidence_score": 0.85,
            "counselor_type": "pastor/missionary/counselor",
            "transition_message": "gentle message explaining why human guidance would be better"
        }
        
        If you include anything other than a pure JSON object, it will be considered invalid.
        Do not include any greetings, explanations, or extra text. Only the JSON object is allowed.
        """
    
    def evaluate_handoff(self, current_message: str, agent_response: str, 
                        conversation_context: list, agent_type: str) -> dict:
        """현재 대화 상황을 분석하여 핸드오프 필요성 판단"""
        try:
            context_summary = self._build_context_summary(conversation_context, 
                                                         current_message, 
                                                         agent_response, 
                                                         agent_type)
            
            judgment_prompt = f"""
            CONVERSATION ANALYSIS REQUEST:
            
            Current Context:
            - Agent Type: {agent_type}
            - User Message: "{current_message}"
            - AI Response: "{agent_response}"
            
            Conversation Summary:
            {context_summary}
            
            Should we transfer to a human counselor?
            Provide your assessment in the required JSON format.
            """
            
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content([
                {"role": "user", "parts": [self.system_prompt]},
                {"role": "user", "parts": [judgment_prompt]}
            ])

            content = response.text
            judgment = json.loads(content)
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
        
        recent_context = conversation_context[-5:] if len(conversation_context) > 5 else conversation_context
        
        summary_parts = [
            f"Conversation Length: {len(conversation_context)} turns",
            f"Current Agent: {agent_type}",
            "\nRecent Conversation:"
        ]
        
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
            "transition_message": judgment.get("transition_message", "")
        }
        
        if validated["urgency_level"] == "CRITICAL":
            validated["handoff_needed"] = True
        return validated
    
    def _get_default_judgment(self) -> dict:
        """에러 발생 시 기본 판단"""
        return {
            "handoff_needed": False,
            "urgency_level": "LOW",
            "primary_reason": "System error - continuing with AI",
            "confidence_score": 0.3,
            "counselor_type": "counselor",
            "transition_message": ""
        }
    
    def generate_handoff_message(self, judgment: dict) -> str:
        """핸드오프 제안 메시지 생성"""
        if not judgment["handoff_needed"]:
            return ""
        
        urgency = judgment["urgency_level"]
        counselor_type = judgment["counselor_type"]
        
        if urgency == "HIGH":
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
            "missionary": "a missionary counselor"
        }
        return descriptions.get(counselor_type, "a professional counselor")
