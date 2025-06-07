# =============================================================================
# 11. 엑셀 파일 관련 유틸리티 함수들
# =============================================================================

def create_sample_excel_file(filename: str = "sample_qa_data.xlsx"):
    """샘플 QnA 데이터로 엑셀 파일 생성"""
    # 샘플 데이터를 pandas DataFrame으로 변환
    df = pd.DataFrame(sample_qa_data)
    df.to_excel(filename, index=False)
    print(f"Sample Excel file created: {filename}")
    print(f"📋 Columns: Question_ENG, Answer_ENG")
    print(f"📊 Rows: {len(sample_qa_data)}")
    return filename

def validate_excel_format(file_path: str) -> bool:
    """엑셀 파일 형식 검증"""
    try:
        df = pd.read_excel(file_path)
        df.columns = df.columns.str.strip().str.lower()
        
        required_columns = ['question_eng', 'answer_eng']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ Missing required columns: {missing_columns}")
            print(f"📋 Available columns: {list(df.columns)}")
            print(f"💡 Expected columns: Question_ENG, Answer_ENG")
            return False
        
        # 빈 값 확인
        empty_questions = df['question_eng'].isna().sum()
        empty_answers = df['answer_eng'].isna().sum()
        
        if empty_questions > 0 or empty_answers > 0:
            print(f"⚠️  Warning: Found {empty_questions} empty questions and {empty_answers} empty answers")
        
        print(f"✅ Excel file format is valid. Found {len(df)} rows.")
        print(f"📋 Columns: {list(df.columns)}")
        return True
        
    except Exception as e:
        print(f"❌ Error validating Excel file: {e}")
        return False

def preview_excel_data(file_path: str, num_rows: int = 5):
    """엑셀 파일 데이터 미리보기"""
    try:
        df = pd.read_excel(file_path)
        print(f"📊 Preview of {file_path} (first {num_rows} rows):")
        print("=" * 80)
        print(df.head(num_rows).to_string(index=False))
        print("=" * 80)
        print(f"Total rows: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        
    except Exception as e:
        print(f"❌ Error previewing Excel file: {e}")

# =============================================================================
# 12. 추가 유틸리티 함수들
# =============================================================================

def export_session_history(chatbot: ChatbotSystem, session_id: str = "default", filename: str = "session_history.json"):
    """세션 히스토리를 JSON 파일로 내보내기"""
    history = chatbot.get_session_history(session_id)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    print(f"Session history exported to {filename}")

def analyze_agent_usage(chatbot: ChatbotSystem, session_id: str = "default"):
    """Agent 사용 통계 분석"""
    history = chatbot.get_session_history(session_id)
    
    if not history:
        print("No conversation history found.")
        return
    
    agent_counts = {}
    for entry in history:
        agent_type = entry['agent_type']
        agent_counts[agent_type] = agent_counts.get(agent_type, 0) + 1
    
    print("Agent Usage Statistics:")
    for agent, count in agent_counts.items():
        print(f"  {agent}: {count} messages")

def add_custom_qa_to_excel(file_path: str, question: str, answer: str):
    """엑셀 파일에 새로운 QnA 추가"""
    try:
        # 기존 파일 읽기
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
        else:
            df = pd.DataFrame(columns=['Question_ENG', 'Answer_ENG'])
        
        # 새 행 추가
        new_row = pd.DataFrame({
            'Question_ENG': [question],
            'Answer_ENG': [answer]
        })
        
        df = pd.concat([df, new_row], ignore_index=True)
        
        # 파일 저장
        df.to_excel(file_path, index=False)
        print(f"✅ Added new Q&A to {file_path}")
        
    except Exception as e:
        print(f"❌ Error adding Q&A to Excel file: {e}")

# 사용 예시:
# add_custom_qa_to_excel("qa_counseling_data.xlsx", "How do I pray?", "Prayer is simply talking to God...")