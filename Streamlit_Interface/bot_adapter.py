
# bot_adapter.py
# ---------------
# Adapter layer to connect your existing chatbot to the Streamlit UI.
#
# Implement get_bot_reply() so it calls *your* bot and returns a string.
#
# Three common patterns are shown below. Uncomment the one you use.

from typing import List, Dict

# Globals to hold expensive resources (models, retrievers, clients, etc.)
_BOT = None


def load_bot_once():
    """
    Initialize heavy resources once per process.
    Put your model/chain/client creation here.
    Example for LangChain / OpenAI / local model is omitted.
    """
    global _BOT
    if _BOT is not None:
        return

    # --- Example A: import your python class/function ---
    # from Chatbot_ver2.chatbot_py import build_chain  # <- your module
    # _BOT = build_chain()  # store for reuse

    # --- Example B: create a simple callable for demo ---
    _BOT = "echo"


def get_bot_reply(message: str, history: List[Dict[str, str]]) -> str:
    """
    Called by Streamlit app every time the user sends a message.

    Parameters
    ----------
    message : str
        Latest user input
    history : List[Dict[str, str]]
        All messages so far in the format: {"role": "user"/"bot", "content": "text"}

    Returns
    -------
    str
        Bot's reply text (plain string).

    TODO: Replace the demo logic with your real bot call.
    """
    global _BOT
    if _BOT is None:
        load_bot_once()

    # --- Example A: call your LangChain Runnable / chain ---
    # response = _BOT.invoke({
    #     "input": message,
    #     "history": history,
    # })
    # return response if isinstance(response, str) else str(response)

    # --- Example B: call a plain Python function ---
    # from Chatbot_ver2.chatbot_py import answer
    # return answer(message, history)

    # --- Example C: call a REST API ---
    # import requests
    # r = requests.post("http://localhost:8000/chat", json={"message": message, "history": history}, timeout=30)
    # r.raise_for_status()
    # return r.json()["reply"]

    # Fallback demo: echo
    return f"Echo: {message}"
