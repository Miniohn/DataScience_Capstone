class ChatbotSystem:
    def __init__(self):
        """챗봇 시스템 초기화"""
        # RAG 시스템 초기화
        self.rag_system = RAGSystem()
        
        # 각 Agent 초기화
        self.orchestrator = OrchestratorAgent()
        self.block_agent = BlockAgent()
        self.counseling_agent = CounselingAgent()
        self.pastor_agent = PastorAgent(self.rag_system)
        
        # 세션 관리
        self.sessions = {}
        
        logger.info("Chatbot system initialized successfully")
    
    def load_qa_dataset(self, qa_data: List[Dict]):
        """QnA 데이터셋 로드"""
        qa_objects = [QnAData(question=item['question'], 
                             answer=item['answer'], 
                             category=item.get('category', 'general')) 
                     for item in qa_data]
        
        self.rag_system.add_qa_data(qa_objects)
        logger.info(f"Loaded {len(qa_objects)} Q&A pairs into the system")
    
    def process_message(self, user_input: str, session_id: str = "default") -> str:
        """사용자 메시지 처리"""
        try:
            # 1. Orchestrator로 주제 분석
            agent_type = self.orchestrator.analyze_topic(user_input)
            logger.info(f"Message routed to: {agent_type.value}")
            
            # 2. 적절한 Agent로 라우팅
            if agent_type == AgentType.BLOCK:
                response = self.block_agent.process(user_input)
                # 차단 Agent에서 None을 반환하면 상담 Agent로 재라우팅
                if response is None:
                    response = self.counseling_agent.process(user_input, session_id)
            elif agent_type == AgentType.COUNSELING:
                response = self.counseling_agent.process(user_input, session_id)
            elif agent_type == AgentType.GOSPEL:
                response = self.pastor_agent.process(user_input)
            else:
                response = "I'm here to help you. Please tell me what's on your mind."
            
            # 3. 세션 히스토리 업데이트
            if session_id not in self.sessions:
                self.sessions[session_id] = []
            
            self.sessions[session_id].append({
                "user_input": user_input,
                "agent_type": agent_type.value,
                "response": response,
                "timestamp": pd.Timestamp.now().isoformat()
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return ("I apologize, but I'm experiencing some technical difficulties. "
                   "Please try again, and know that I'm here to support you.")
    
    def get_session_history(self, session_id: str = "default") -> List[Dict]:
        """세션 히스토리 조회"""
        return self.sessions.get(session_id, [])
    
    def reset_session(self, session_id: str = "default"):
        """세션 초기화"""
        if session_id in self.sessions:
            del self.sessions[session_id]
        self.counseling_agent.reset_conversation(session_id)
