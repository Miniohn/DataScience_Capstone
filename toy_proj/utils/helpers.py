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

def add_custom_qa(chatbot: ChatbotSystem, question: str, answer: str, category: str = "custom"):
    """커스텀 QnA 추가"""
    qa_data = [{"question": question, "answer": answer, "category": category}]
    chatbot.load_qa_dataset(qa_data)
    print(f"Added custom Q&A: {question}")
