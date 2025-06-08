import pandas as pd
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

def load_from_excel(file_path: str) -> List[Dict]:
        """엑셀 파일에서 QnA 데이터 로드"""
        try:
            df = pd.read_excel(file_path)
            df.columns = df.columns.str.strip().str.lower()
            
            required_columns = ['question_eng', 'answer_eng']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                available_cols = list(df.columns)
                raise ValueError(f"Missing required columns: {missing_columns}. Available columns: {available_cols}")
            
            df = df.dropna(subset=['question_eng', 'answer_eng'])
            
            qa_data = []
            for _, row in df.iterrows():
                qa_item = {
                    'question': str(row['question_eng']).strip(),
                    'answer': str(row['answer_eng']).strip(),
                    'category': 'general'
                }
                qa_data.append(qa_item)
            
            logger.info(f"Successfully loaded {len(qa_data)} Q&A pairs from Excel file: {file_path}")
            return qa_data
            
        except Exception as e:
            logger.error(f"Error loading Excel file {file_path}: {e}")
            raise
        
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

'''
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
'''