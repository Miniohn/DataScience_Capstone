"""Evan AI Streamlit UI → 검증된 공통 RAG/ LangGraph 코어 연결."""
import sys
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from rag_core import run


def load_bot_once():
    """rag_core import 시 모델 및 저장된 ChromaDB 초기화."""
    return None


def get_bot_reply(message: str, history: List[Dict], session_id: str) -> str:
    """실패 시 가짜 답변을 반환하지 않고 에러를 명확히 노출."""
    state = run(message, session_id)
    if not isinstance(state, dict):
        raise RuntimeError(f"잘못된 응답 상태: {type(state).__name__}")
    if state.get("error"):
        raise RuntimeError(str(state["error"]))
    return state.get("final_translated") or state.get("generation") or "응답 내용이 없습니다."
