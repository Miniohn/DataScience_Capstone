# app/chatbot_system.py
import logging
from datetime import datetime
from typing import List, Dict
import pandas as pd

# 모델과 유틸리티 임포트
from app.models import AgentType, HandoffUrgency, HandoffRequest, QnAData
from app.utils.excel_loader import load_from_excel

# Agent들 임포트
from app.agents.orchestrator_agent import OrchestratorAgent
from app.agents.block_agent import BlockAgent
from app.agents.counseling_agent import CounselingAgent
from app.agents.pastor_agent import PastorAgent, RAGSystem
from app.agents.handoff_judge_agent import HandoffJudgeAgent

# 통합 서비스 임포트
from app.integrations.notification_manager import WhatsAppNotificationManager

logger = logging.getLogger(__name__)

class ChatbotSystem:
    def __init__(self):
        """챗봇 시스템 초기화"""
        self.rag_system = RAGSystem()
        self.notification_manager = WhatsAppNotificationManager()
        self.orchestrator = OrchestratorAgent()
        self.block_agent = BlockAgent()
        self.counseling_agent = CounselingAgent()
        self.pastor_agent = PastorAgent(self.rag_system)
        self.handoff_judge = HandoffJudgeAgent()
        self.sessions = {}
        self.active_handoffs = {}
        logger.info("Integrated chatbot system initialized successfully")

    def load_qa_dataset(self, excel_file_path: str):
        qa_data = load_from_excel(excel_file_path)
        if not qa_data:
            logger.warning("No QnA data loaded")
            return
        
        qa_objects = [QnAData(question=item['question'], 
                             answer=item['answer'], 
                             category=item.get('category', 'general')) 
                     for item in qa_data]
        
        self.rag_system.add_qa_data(qa_objects)
        logger.info(f"Loaded {len(qa_objects)} Q&A pairs into the system")
    
    def process_message(self, user_input: str, session_id: str = "default") -> dict:
        """사용자 메시지 처리 (핸드오프 판단 포함)"""
        try:
            # 1. Orchestrator로 주제 분석
            agent_type = self.orchestrator.analyze_topic(user_input)
            logger.info(f"Message routed to: {agent_type.value}")
            
            # 2. 적절한 Agent로 라우팅하여 응답 생성
            if agent_type == AgentType.BLOCK:
                agent_response = self.block_agent.process(user_input)
                if agent_response is None:
                    agent_response = self.counseling_agent.process(user_input, session_id)
                    agent_type = AgentType.COUNSELING
            elif agent_type == AgentType.COUNSELING:
                agent_response = self.counseling_agent.process(user_input, session_id)
            elif agent_type == AgentType.GOSPEL:
                agent_response = self.pastor_agent.process(user_input)
            else:
                agent_response = "I'm here to help you. Please tell me what's on your mind."
            
            # 3. 세션 히스토리 가져오기
            conversation_context = self.get_session_history(session_id)
            
            # 4. Handoff Judge Agent로 핸드오프 필요성 판단
            handoff_judgment = self.handoff_judge.evaluate_handoff(
                current_message=user_input,
                agent_response=agent_response,
                conversation_context=conversation_context,
                agent_type=agent_type.value
            )
            
            # 5. 핸드오프 메시지 생성 (필요한 경우)
            handoff_message = ""
            if handoff_judgment["handoff_needed"]:
                handoff_message = self.handoff_judge.generate_handoff_message(handoff_judgment)
                
                # WhatsApp 알림 전송
                handoff_request = HandoffRequest(
                    user_phone=session_id,  # 실제로는 사용자 전화번호
                    user_message=user_input,
                    urgency=HandoffUrgency(handoff_judgment["urgency_level"]),
                    reason=handoff_judgment["primary_reason"],
                    counselor_type=handoff_judgment["counselor_type"],
                    timestamp=datetime.now().isoformat(),
                    conversation_summary="",  # 실제로는 대화 요약
                    session_id=session_id
                )
                
                self.active_handoffs[session_id] = handoff_request
                self.notification_manager.send_handoff_notifications(handoff_request)
            
            # 6. 최종 응답 구성
            final_response = agent_response
            if handoff_message:
                final_response += f"\n\n{handoff_message}"
            
            # 7. 세션 히스토리 업데이트
            if session_id not in self.sessions:
                self.sessions[session_id] = []
            
            self.sessions[session_id].append({
                "user_input": user_input,
                "agent_type": agent_type.value,
                "response": agent_response,
                "handoff_judgment": handoff_judgment,
                "final_response": final_response,
                "timestamp": datetime.now().isoformat()
            })
            
            # 8. 결과 반환
            return {
                "response": final_response,
                "agent_type": agent_type.value,
                "handoff_needed": handoff_judgment["handoff_needed"],
                "handoff_urgency": handoff_judgment["urgency_level"],
                "handoff_reason": handoff_judgment["primary_reason"],
                "counselor_type": handoff_judgment["counselor_type"],
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "response": ("I apologize, but I'm experiencing some technical difficulties. "
                           "Please try again, and know that I'm here to support you."),
                "agent_type": "ERROR",
                "handoff_needed": False,
                "handoff_urgency": "LOW",
                "handoff_reason": "System error",
                "counselor_type": "counselor",
                "session_id": session_id
            }
    
    def get_session_history(self, session_id: str = "default") -> List[Dict]:
        """세션 히스토리 조회"""
        return self.sessions.get(session_id, [])
    
    def reset_session(self, session_id: str = "default"):
        """세션 초기화"""
        if session_id in self.sessions:
            del self.sessions[session_id]
        self.counseling_agent.reset_conversation(session_id)