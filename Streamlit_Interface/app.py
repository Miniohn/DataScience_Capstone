import sys
try:
    import pysqlite3
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    import sqlite3

from datetime import datetime
from typing import List, Dict
import html
import streamlit as st
from streamlit.components.v1 import html as st_html

# --- bot adapter 연결 ---
try:
    from bot_adapter import get_bot_reply, load_bot_once
    load_bot_once()  # 최초 로드
    print("✅ Bot adapter loaded successfully")
except Exception as e:
    print(f"❌ Bot adapter load failed: {e}")
    st.error(f"Bot loading error: {e}")  # Streamlit에서 오류 표시
    
    def get_bot_reply(message: str, history: List[Dict[str, str]]) -> str:
        return f"(demo) You said: {message}"
    def load_bot_once():
        pass


except Exception as e:
    def get_bot_reply(message: str, history: List[Dict[str, str]]) -> str:
        return f"(demo) You said: {message}"
    def load_bot_once():
        pass

# --- Streamlit 설정 ---
st.set_page_config(
    page_title="WhatsApp-style Chatbot",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 상태 관리
if "messages" not in st.session_state:
    st.session_state.messages = []
if "draft" not in st.session_state:
    st.session_state.draft = ""
if "initialized" not in st.session_state:
    try:
        load_bot_once()
    except Exception as e:
        st.toast(f"Bot load failed: {e}", icon="⚠️")
    st.session_state.initialized = True

def now_hhmm():
    return datetime.now().strftime("%H:%M")

def add_message(sender: str, text: str | None):
    st.session_state.messages.append({"sender": sender, "text": text, "time": now_hhmm()})

# --- 입력창 과거 기록 박스 숨기기 ---
hide_input_history = """
<style>
.stTextInput [data-baseweb="popover"] {
    display: none !important;
}
</style>
"""
st.markdown(hide_input_history, unsafe_allow_html=True)

# --- CSS (WhatsApp 스타일) ---
whatsapp_css = '''
<style>
:root{
  --bg:#0e1a20;
  --header-bg:#11605a;
  --user-bubble:#25D366;
  --bot-bubble:#26343c;
}

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="block-container"]{
  background: var(--bg) !important;
}
.block-container{ padding-top:1rem !important; padding-bottom:0 !important; }

.chat-wrap {
  width:480px; max-width:100%;
  margin:0 auto; 
  border-radius:14px;
  box-shadow:0 8px 20px rgba(0,0,0,0.10);
  overflow:hidden;
  background: var(--bg) !important;
  border:1px solid rgba(255,255,255,0.06);
}

.header {
  background: var(--header-bg); color:#fff; padding:12px 14px;
  display:flex; align-items:center; gap:12px;
}
.header .avatar { width:36px; height:36px; border-radius:50%; background:#c2e9e2; display:inline-block;}
.header .name{ font-weight:600; } .header .status{font-size:12px; color:#d7fff3;} .header .spacer{flex:1;}
.header .icons{opacity:.95; font-size:18px; display:flex; gap:12px;}

.chat-area {
  display:flex; flex-direction:column; justify-content:flex-start;
  height:auto; 
  max-height:70vh;
  padding:4px 12px 4px; 
  overflow-y:auto;
  background: var(--bg) !important;
}

.msg{ display:flex; align-items:flex-end; margin:4px 0; }
.msg.user{justify-content:flex-end;} .msg.bot{justify-content:flex-start;}

.bubble{
  max-width:78%;
  padding:8px 10px; 
  border-radius:14px;
  word-wrap:break-word; white-space:pre-wrap;
  box-shadow:0 1px 0 rgba(0,0,0,.10);
  font-size:15px; line-height:1.38;
  border:1px solid rgba(255,255,255,0.06);
}
.bubble.user{ background: var(--user-bubble); color:#fff; border-top-right-radius:6px;}
.bubble.bot{  background: var(--bot-bubble);  color:#E9EDEF; border-top-left-radius:6px;}

.time-outside{
  font-size:11px; color:rgba(233,237,239,0.7);
  margin-left:6px;
}

.input-bar{
  display:flex; gap:8px; padding:8px 10px;
  background: var(--bg) !important;
  border-top:0 !important;
}

.stTextInput, .stTextArea{ background:transparent !important; }
.stTextInput > div, .stTextArea > div,
.stTextInput > div > div, .stTextArea > div > div{
  background:transparent !important; box-shadow:none !important; border:none !important; padding:0 !important;
}
.stTextInput [data-baseweb="input"],
.stTextInput [data-baseweb="base-input"]{
  background:transparent !important; box-shadow:none !important; border:none !important;
}

.input-bar input, .input-bar textarea,
.stTextInput input, .stTextArea textarea{
  width:100% !important;
  background:#2a3942 !important; color:#e9edef !important;
  border:1px solid #3b4a54 !important; border-radius:18px !important;
  padding:10px 12px !important; outline:none !important;
}
.input-bar input::placeholder, .stTextInput input::placeholder{ color:#95a5ae; opacity:1; }

.input-bar div.stButton > button{
  background:#25D366 !important; color:#0b141a !important;
  border:none !important; border-radius:14px !important; padding:8px 14px !important;
  font-weight:700; cursor:pointer;
}
.input-bar div.stButton > button:hover{
  background:#1ebe5b !important; color:#0b141a !important;
}
.input-bar div.stButton > button:focus{
  box-shadow:0 0 0 3px rgba(37,211,102,.35) !important; outline:none !important;
}

@media (max-width:480px){
  .chat-wrap{border-radius:0;}
  .chat-area{max-height:68vh;}
}
</style>
'''
st.markdown(whatsapp_css, unsafe_allow_html=True)

st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)

# --- Header ---
st.markdown('''
<div class="header">
  <div class="avatar"></div>
  <div>
    <div class="name">Gabriela Silva</div>
    <div class="status">online</div>
  </div>
  <div class="spacer"></div>
  <div class="icons">📞 🎥 ⋮</div>
</div>
''', unsafe_allow_html=True)

# --- Chat area ---
st.markdown('<div id="chat-area" class="chat-area">', unsafe_allow_html=True)

for m in st.session_state.messages:
    text = (m.get("text") or "").strip()
    if not text:
        continue
    role = "user" if m.get("sender") == "user" else "bot"
    bubble_class = "bubble user" if role == "user" else "bubble bot"
    safe_text = html.escape(text)
    time_txt = html.escape(m.get("time",""))
    st.markdown(
        f'''
        <div class="msg {role}">
          <div class="{bubble_class}">{safe_text}</div>
          <div class="time-outside">{time_txt}</div>
        </div>
        ''',
        unsafe_allow_html=True
    )

st_html("""
<script>
  setTimeout(() => {
    const area = window.parent.document.getElementById('chat-area');
    if (!area) return;
    area.scrollTop = area.scrollHeight;
  }, 0);
</script>
""", height=0)

st.markdown('</div>', unsafe_allow_html=True)

# --- Input bar ---
st.markdown('<div class="input-bar">', unsafe_allow_html=True)
col1, col2 = st.columns([5, 1])
with col1:
    st.session_state.draft = st.text_input(
        "Type a message",
        value=st.session_state.draft,
        placeholder="Type a message",
        label_visibility="collapsed"
    )
with col2:
    send_clicked = st.button("Send", key="send", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 메시지 전송 처리 ---
if send_clicked:
    msg = (st.session_state.draft or "").strip()
    if msg:
        add_message("user", msg)
        with st.spinner("Thinking..."):
            history_for_bot = [
                {"role": m["sender"], "content": (m.get("text") or "")}
                for m in st.session_state.messages
                if (m.get("text") or "").strip()
            ]
            bot_reply = get_bot_reply(msg, history_for_bot)
            reply_text = (bot_reply or "").strip()
            if reply_text:
                add_message("bot", reply_text)
            else:
                st.toast("No reply (blocked or empty).", icon="🛑")
        st.session_state.draft = ""
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

##