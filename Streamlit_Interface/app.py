
import time
from datetime import datetime
from typing import List, Dict

import streamlit as st

# --- Try to import the user's bot adapter ---
try:
    from bot_adapter import get_bot_reply, load_bot_once
except Exception as e:
    # Fallback: simple echo bot
    def get_bot_reply(message: str, history: List[Dict[str, str]]) -> str:
        return f"(demo) You said: {message}"
    def load_bot_once():
        return None

# --- Page config ---
st.set_page_config(page_title="WhatsApp-style Chatbot", page_icon="💬", layout="centered", initial_sidebar_state="collapsed")

# --- Minimal state ---
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of dicts: {"sender": "user"/"bot", "text": str, "time": "HH:MM"}

if "initialized" not in st.session_state:
    # Load the bot only once (e.g., embeddings/LLM/clients)
    try:
        load_bot_once()
    except Exception as e:
        st.toast(f"Bot load failed: {e}", icon="⚠️")
    st.session_state.initialized = True

# --- Helper functions ---
def now_hhmm():
    return datetime.now().strftime("%H:%M")

def add_message(sender: str, text: str):
    st.session_state.messages.append({"sender": sender, "text": text, "time": now_hhmm()})

# --- Styles to mimic WhatsApp look ---
whatsapp_css = '''
<style>
/* App canvas */
.main > div { padding-top: 0.5rem; }

.chat-wrap {
  width: 420px;
  max-width: 100%;
  margin: 0 auto;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.08);
  overflow: hidden;
  background: #eae6df; /* WhatsApp chat bg-ish */
}

/* Header bar */
.header {
  background: #075E54;
  color: white;
  padding: 10px 12px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.header .avatar {
  width: 34px; height: 34px; border-radius: 50%;
  background: #c2e9e2; display: inline-block;
}
.header .name { font-weight: 600; }
.header .status { font-size: 12px; color: #d7fff3; }
.header .spacer { flex: 1; }
.header .icons { opacity: 0.95; font-size: 18px; display: flex; gap: 12px; }

/* Chat area */
.chat-area {
  background-image: radial-gradient(#d1d7db 1px, transparent 1px);
  background-size: 10px 10px;
  min-height: 60vh;
  padding: 10px;
  overflow-y: auto;
}

/* Bubbles */
.msg {
  display: flex;
  margin: 6px 0;
}
.msg.user { justify-content: flex-end; }
.msg.bot  { justify-content: flex-start; }

.bubble {
  max-width: 78%;
  padding: 8px 10px;
  border-radius: 10px;
  position: relative;
  word-wrap: break-word;
  white-space: pre-wrap;
  box-shadow: 0 1px 0 rgba(0,0,0,0.05);
}

.bubble.user {
  background: #D9FDD3; /* WhatsApp green-ish */
  border-top-right-radius: 2px;
}
.bubble.bot {
  background: #FFFFFF;
  border-top-left-radius: 2px;
}

.time {
  font-size: 11px;
  color: #667781;
  text-align: right;
  margin-top: 4px;
}

/* Input bar */
.input-bar {
  display: flex;
  gap: 8px;
  padding: 10px;
  background: #F0F2F5;
  border-top: 1px solid #E6EBEF;
}
.input-bar textarea {
  flex: 1;
  resize: none !important;
  border: 1px solid #E0E0E0 !important;
  background: white;
  border-radius: 18px;
  padding: 10px 12px;
  min-height: 46px;
}
.send-btn {
  border-radius: 14px;
  padding: 8px 14px;
  background: #25D366;
  color: white;
  border: none;
  font-weight: 600;
  cursor: pointer;
}
.send-btn:hover { filter: brightness(0.95); }

/* Small screen tweak */
@media (max-width: 480px) {
  .chat-wrap { border-radius: 0; }
}
</style>
'''

st.markdown(whatsapp_css, unsafe_allow_html=True)

# --- Render UI ---
with st.container():
    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)

    # Header
    header_html = '''
    <div class="header">
      <div class="avatar"></div>
      <div>
        <div class="name">Gabriela Silva</div>
        <div class="status">online</div>
      </div>
      <div class="spacer"></div>
      <div class="icons">📞 🎥 ⋮</div>
    </div>
    '''
    st.markdown(header_html, unsafe_allow_html=True)

    # Chat area
    st.markdown('<div class="chat-area">', unsafe_allow_html=True)
    for m in st.session_state.messages:
        role = "user" if m["sender"] == "user" else "bot"
        bubble_class = "bubble user" if role == "user" else "bubble bot"
        safe_text = m["text"].replace("<","&lt;").replace(">","&gt;")
        msg_html = f'''
        <div class="msg {role}">
          <div class="{bubble_class}">
            {safe_text}
            <div class="time">{m["time"]}</div>
          </div>
        </div>
        '''
        st.markdown(msg_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # end chat-area

    # Input bar
    with st.form(key="input-form", clear_on_submit=True):
        st.markdown('<div class="input-bar">', unsafe_allow_html=True)
        user_text = st.text_area("Type a message", placeholder="Type a message", height=46, label_visibility="collapsed")
        submitted = st.form_submit_button("Send", use_container_width=False)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # end chat-wrap

# --- Handle send ---
if submitted and user_text.strip():
    add_message("user", user_text.strip())
    with st.spinner("Thinking..."):
        try:
            # Pass message + full history (without timestamps) to the bot
            history_for_bot = [{"role": m["sender"], "content": m["text"]} for m in st.session_state.messages]
            bot_reply = get_bot_reply(user_text.strip(), history_for_bot)
        except Exception as e:
            bot_reply = f"⚠️ Bot error: {e}"
        time.sleep(0.15)
        add_message("bot", bot_reply)

    st.rerun()
