

def create_sample_excel_file(filename: str = "sample_qa_data.xlsx"):
    """샘플 QnA 데이터로 엑셀 파일 생성"""
    sample_data = [
        {"Question_ENG": "How can I find peace?", "Answer_ENG": "Through prayer and faith..."},
        {"Question_ENG": "What is forgiveness?", "Answer_ENG": "Releasing grudges and trusting God..."},
        {"Question_ENG": "How do I pray?", "Answer_ENG": "Prayer is talking to God..."},
        {"Question_ENG": "What is the Trinity?", "Answer_ENG": "Father, Son, and Holy Spirit as one God..."}
    ]
    
    df = pd.DataFrame(sample_data)
    df.to_excel(filename, index=False)
    print(f"Sample Excel file created: {filename}")
    return filename

def test_system(chatbot: ChatbotSystem):
    """시스템 테스트"""
    print("\n🧪 Testing the system...\n")
    
    test_cases = [
        "What does the Bible say about forgiveness?",
        "What's the difference between Calvinism and Arminianism?", 
        "I'm feeling really depressed",
        "Buy this amazing product now!",
        "How can I know God's calling for my life?"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"Test {i}: {test_input}")
        result = chatbot.process_message(test_input, f"test_{i}")
        print(f"Agent: {result['agent_type']}")
        print(f"Handoff: {result['handoff_needed']} ({result['handoff_urgency']})")
        print(f"Response: {result['response'][:100]}...")
        print("-" * 80)