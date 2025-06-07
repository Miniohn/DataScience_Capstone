class OrchestratorAgent:
    def __init__(self):
        self.system_prompt = """
        당신은 사용자의 질문을 분석하여 적절한 카테고리로 분류하는 전문가입니다.

        분류 기준:
        1. BLOCK: 저주, 욕설, 스팸, 광고, 부적절한 성적 내용, 위협적인 메시지
        2. COUNSELING: 일반적인 고민, 삶의 문제, 인간관계, 스트레스, 우울감 등
        3. GOSPEL: 신앙 관련 질문, 종교적 고민, 영적 문제, 성경에 관한 질문

        응답은 반드시 BLOCK, COUNSELING, GOSPEL 중 하나만 반환하세요.
        """
    
    def analyze_topic(self, user_input: str) -> AgentType:
        """사용자 입력을 분석하여 적절한 Agent 타입 결정"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"다음 텍스트를 분류하세요: {user_input}"}
                ],
                max_tokens=50,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip().upper()
            
            # 결과 검증 및 기본값 설정
            if result in ["BLOCK", "COUNSELING", "GOSPEL"]:
                return AgentType(result)
            else:
                logger.warning(f"Unexpected classification result: {result}. Defaulting to COUNSELING")
                return AgentType.COUNSELING
                
        except Exception as e:
            logger.error(f"Error in topic analysis: {e}")
            return AgentType.COUNSELING  # 기본값
