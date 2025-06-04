from core.chatbot import ChatbotSystem

def initialize_system():
    """시스템 초기화"""
    print("🚀 Initializing Multi-Agent Counseling System...")
    
    # 시스템 생성
    chatbot = ChatbotSystem()
    
    # 샘플 데이터 로드
    chatbot.load_qa_dataset(sample_qa_data)
    
    print("✅ System initialized successfully!")
    return chatbot

def test_system(chatbot: ChatbotSystem):
    """시스템 테스트"""
    print("\n🧪 Testing the system with sample queries...\n")
    
    test_cases = [
        "I'm feeling really depressed and don't know what to do",  # COUNSELING
        "What does the Bible say about finding hope?",            # GOSPEL
        "Buy this amazing product now! Click here!",              # BLOCK
        "How can I deal with stress at work?",                    # COUNSELING
        "Is God real? I'm having doubts about my faith"          # GOSPEL
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"Test {i}: {test_input}")
        response = chatbot.process_message(test_input, f"test_session_{i}")
        print(f"Response: {response}\n")
        print("-" * 80 + "\n")

if __name__ == "__main__":
    # 시스템 초기화
    chatbot_system = initialize_system()
    
    # 테스트 실행
    test_system(chatbot_system)
    
    # 대화형 모드 (옵션)
    print("💬 Interactive mode started. Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Thank you for using the Multi-Agent Counseling System. May God bless you!")
            break
        
        response = chatbot_system.process_message(user_input)
        print(f"Assistant: {response}\n")
