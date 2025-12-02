# streamlit/bot_adapter.py
from typing import List, Dict
import os
import sys

# --- revised.py 를 import 할 수 있게 경로 추가 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))      # .../Chatbot_ver2/streamlit
PROJECT_DIR = os.path.dirname(BASE_DIR)                    # .../Chatbot_ver2
if PROJECT_DIR not in sys.path:
    sys.path.append(PROJECT_DIR)

# 이제 상위 폴더에 있는 revised.py import
from demo import run

_BOT_INITIALIZED = False

def load_bot_once():
    """지금 구조에서는 별도 초기화는 필요 없지만, app.py와 인터페이스 맞추기용."""
    global _BOT_INITIALIZED
    if _BOT_INITIALIZED:
        return
    # revised.py는 import 되는 순간 RAG, 그래프 등을 세팅함
    _BOT_INITIALIZED = True

def get_bot_reply(message: str, history: List[Dict[str, str]]) -> str:
    """
    Streamlit에서 호출하는 챗봇 인터페이스.
    message: 사용자의 최신 발화
    history: 이전 대화 (지금은 사용하지 않지만 형태만 맞춰 둠)
    """
    try:
        load_bot_once()
        session_id = "streamlit_session"  # 한 브라우저에서 하나의 세션으로 묶기

        # revised.run은 (state)를 반환하도록 수정해 둘 것
        final_state = run(message, session_id)

        if isinstance(final_state, dict):
            text = (
                final_state.get("final_translated")
                or final_state.get("generation")
                or ""
            )
            return text or "🛑 Empty reply."
        else:
            return str(final_state)

    except Exception as e:
        return f"⚠️ Bot error: {e}"
