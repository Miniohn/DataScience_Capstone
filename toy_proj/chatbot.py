

# =============================================================================
# 8. 메인 챗봇 시스템
# =============================================================================

class ChatbotSystem:
    def __init__(self):
        """챗봇 시스템 초기화"""
        # RAG 시스템 초기화
        self.rag_system = RAGSystem()
        
        # WhatsApp 알림 시스템 초기화
        self.notification_manager = WhatsAppNotificationManager()
        
        # 각 Agent 초기화
        self.orchestrator = OrchestratorAgent()
        self.block_agent = BlockAgent()
        self.counseling_agent = CounselingAgent()
        self.pastor_agent = PastorAgent(self.rag_system)
        self.handoff_judge = HandoffJudgeAgent()  # 새로운 Agent 추가
        
        # 세션 관리
        self.sessions = {}
        self.active_handoffs = {}  # 진행 중인 핸드오프 추적
        
        logger.info("Integrated chatbot system with WhatsApp handoff initialized successfully")
    
    def load_qa_dataset(self, qa_data: List[Dict] = None, excel_file_path: str = None):
        """QnA 데이터셋 로드 (리스트 또는 엑셀 파일에서)"""
        if excel_file_path:
            # 엑셀 파일에서 데이터 로드 (컬럼명: Question_ENG, Answer_ENG)
            qa_data = self._load_from_excel(excel_file_path)
        
        if not qa_data:
            logger.warning("No QnA data provided")
            return
        
        qa_objects = [QnAData(question=item['question'], 
                             answer=item['answer'], 
                             category=item.get('category', 'general')) 
                     for item in qa_data]
        
        self.rag_system.add_qa_data(qa_objects)
        logger.info(f"Loaded {len(qa_objects)} Q&A pairs into the system")
    
    def _load_from_excel(self, file_path: str) -> List[Dict]:
        """엑셀 파일에서 QnA 데이터 로드"""
        try:
            # 엑셀 파일 읽기
            df = pd.read_excel(file_path)
            
            # 컬럼명 정규화 (대소문자 무시, 공백 제거)
            df.columns = df.columns.str.strip().str.lower()
            
            # 필수 컬럼 확인 (Question_ENG, Answer_ENG)
            required_columns = ['question_eng', 'answer_eng']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                available_cols = list(df.columns)
                raise ValueError(f"Missing required columns: {missing_columns}. Available columns: {available_cols}")
            
            # 빈 행 제거
            df = df.dropna(subset=['question_eng', 'answer_eng'])
            
            # 딕셔너리 리스트로 변환
            qa_data = []
            for _, row in df.iterrows():
                qa_item = {
                    'question': str(row['question_eng']).strip(),
                    'answer': str(row['answer_eng']).strip(),
                    'category': 'general'  # 기본 카테고리로 설정
                }
                
                qa_data.append(qa_item)
            
            logger.info(f"Successfully loaded {len(qa_data)} Q&A pairs from Excel file: {file_path}")
            return qa_data
            
        except Exception as e:
            logger.error(f"Error loading Excel file {file_path}: {e}")
            raise
    
    def process_message(self, user_input: str, session_id: str = "default") -> dict:
        """사용자 메시지 처리 (핸드오프 판단 포함)"""
        try:
            # 1. Orchestrator로 주제 분석
            agent_type = self.orchestrator.analyze_topic(user_input)
            logger.info(f"Message routed to: {agent_type.value}")
            
            # 2. 적절한 Agent로 라우팅하여 응답 생성
            if agent_type == AgentType.BLOCK:
                agent_response = self.block_agent.process(user_input)
                # 차단 Agent에서 None을 반환하면 상담 Agent로 재라우팅
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
                "timestamp": pd.Timestamp.now().isoformat()
            })
            
            # 8. 결과 반환 (응답 + 메타데이터)
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
