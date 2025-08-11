# app.py — WhatsApp 스타일 UI (None 응답 안전처리 포함)
import time
from datetime import datetime
from typing import List, Dict
import html
import streamlit as st

# --- bot adapter ---
try:
    from bot_adapter import get_bot_reply, load_bot_once
except Exception:
    def get_bot_reply(message: str, history: List[Dict[str, str]]) -> str:
        return f"(demo) You said: {message}"
    def load_bot_once():
        pass

st.set_page_config(page_title="WhatsApp-style Chatbot", page_icon="💬", layout="centered", initial_sidebar_state="collapsed")

# 상태
if "messages" not in st.session_state:
    st.session_state.messages = []   # {"sender": "user"/"bot", "text": str|None, "time": "HH:MM"}
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

# --- 스타일 ---
whatsapp_css = '''
<style>
.main > div { padding-top: 0.5rem; }
.chat-wrap { width: 420px; max-width: 100%; margin: 0 auto; border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.08); overflow: hidden; background: #111b21; }
.header { background:#075E54; color:#fff; padding:10px 12px; display:flex; align-items:center; gap:10px; }
.header .avatar { width:34px; height:34px; border-radius:50%; background:#c2e9e2; display:inline-block;}
.header .name{ font-weight:600;} .header .status{font-size:12px; color:#d7fff3;} .header .spacer{flex:1;}
.header .icons{opacity:.95; font-size:18px; display:flex; gap:12px;}
.chat-area { min-height:60vh; max-height:70vh; padding:16px 12px 18px; overflow-y:auto; background:#0b141a; }
.msg{ display:flex; margin:10px 0; } .msg.user{justify-content:flex-end;} .msg.bot{justify-content:flex-start;}
.bubble{ max-width:78%; padding:10px 12px; border-radius:14px; word-wrap:break-word; white-space:pre-wrap;
  box-shadow:0 1px 0 rgba(0,0,0,.05); font-size:15px; line-height:1.4; color:#111;}
.bubble.user{ background:#D9FDD3; border-top-right-radius:6px;}
.bubble.bot{ background:#FFFFFF; border-top-left-radius:6px;}
.time{ font-size:11px; color:#4f5b60; text-align:right; margin-top:6px;}
.input-bar{ display:flex; gap:8px; padding:10px; background:#202c33; border-top:1px solid #1f2c34;}
.input-bar .stTextInput > div > div input{
  border-radius:18px; padding:10px 12px; background:#2a3942; color:#e9edef; border:1px solid #3b4a54;}
.send-btn > button{ border-radius:14px; padding:8px 14px; background:#25D366; color:white; border:none; font-weight:600;}
.send-btn > button:hover{ filter:brightness(.95); }
@media (max-width:480px){ .chat-wrap{border-radius:0;} }
</style>
'''
st.markdown(whatsapp_css, unsafe_allow_html=True)

# --- UI 렌더 ---
st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)

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

st.markdown('<div class="chat-area">', unsafe_allow_html=True)

# 메시지 렌더링 (None/빈 문자열은 스킵)
for m in st.session_state.messages:
    text = (m.get("text") or "").strip()
    if not text:
        continue
    role = "user" if m.get("sender") == "user" else "bot"
    bubble_class = "bubble user" if role == "user" else "bubble bot"
    safe_text = html.escape(text)
    st.markdown(
        f'''
        <div class="msg {role}">
          <div class="{bubble_class}">
            {safe_text}
            <div class="time">{m.get("time","")}</div>
          </div>
        </div>
        ''',
        unsafe_allow_html=True
    )

st.markdown('</div>', unsafe_allow_html=True)

# 입력/전송
st.markdown('<div class="input-bar">', unsafe_allow_html=True)
col1, col2 = st.columns([5, 1])
with col1:
    st.session_state.draft = st.text_input("Type a message",
                                           value=st.session_state.draft,
                                           placeholder="Type a message",
                                           label_visibility="collapsed")
with col2:
    send_clicked = st.button("Send", key="send", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# 전송 처리 (히스토리도 안전하게 구성)
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

st.markdown('</div>', unsafe_allow_html=True)  # end chat-wrap
