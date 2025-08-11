from typing import List, Dict

_BOT = None  # callable(message, history) -> str

def load_bot_once():
    global _BOT
    if _BOT is not None:
        return
    from chatbot_for_UI import build_chain  # 같은 폴더
    _BOT = build_chain()

def get_bot_reply(message: str, history: List[Dict[str, str]]) -> str:
    global _BOT
    if _BOT is None:
        load_bot_once()
    try:
        return _BOT(message, history)
    except Exception as e:
        return f"⚠️ Bot error: {e}"
