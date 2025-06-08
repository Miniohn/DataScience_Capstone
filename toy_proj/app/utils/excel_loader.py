from app.chatbot_system import ChatbotSystem
import pandas as pd

def create_sample_excel_file(filename: str = "sample_qa_data.xlsx"):
    """샘플 QnA 데이터로 엑셀 파일 생성"""
    sample_data = [
        {
            "question": "How can I find peace in difficult times?",
            "answer": "Finding peace requires turning to God through prayer and meditation. Remember Philippians 4:6-7 about God's peace that transcends understanding."
        },
        {
            "question": "What does the Bible say about forgiveness?",
            "answer": "Forgiveness is central to Christian faith. Jesus taught us to forgive as we have been forgiven (Ephesians 4:32)."
        },
        {
            "question": "How do I know if God loves me?",
            "answer": "God's love is demonstrated through Jesus Christ. Romans 5:8 shows His love isn't based on performance but is unconditional."
        },
        {
            "question": "What is the Trinity?",
            "answer": "The Trinity is the Christian doctrine that God exists as three persons - Father, Son, and Holy Spirit - yet remains one God. This requires deep theological understanding."
        }
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