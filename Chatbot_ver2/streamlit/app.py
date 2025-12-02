import traceback
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
import base64
from pathlib import Path


###############################################################
# BOT LOADING
###############################################################
try:
    from bot_adapter import get_bot_reply, load_bot_once
    load_bot_once()
except:
    def get_bot_reply(message, history): return f"(demo) {message}"


###############################################################
# STREAMLIT PAGE CONFIG
###############################################################
st.set_page_config(
    page_title="Evan AI Chat",
    page_icon="💬",
    layout="wide",
)


###############################################################
# 이미지 로드 함수
###############################################################
def get_image_base64(image_path):
    """로컬 이미지를 base64로 인코딩"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None


###############################################################
# SESSION STATE INIT
###############################################################
if "messages" not in st.session_state:
    st.session_state.messages = []

if "draft" not in st.session_state:
    st.session_state.draft = ""


###############################################################
# CSS STYLING (회색/초록 톤)
###############################################################
# bible.png 이미지 base64 인코딩
img_base64 = get_image_base64("bible.png")
img_src = f"data:image/png;base64,{img_base64}" if img_base64 else "https://via.placeholder.com/90"

css = f"""
<style>
/* 모든 Streamlit 기본 스타일 제거 */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
    background-color: #F8F8F8 !important;
    margin: 0;
    padding: 0;
}}

[data-testid="stHeader"] {{
    background-color: transparent !important;
    display: none !important;
}}

[data-testid="stToolbar"] {{
    display: none !important;
}}

section[data-testid="stSidebar"] {{
    background-color: #EFEFEF !important;
}}

section[data-testid="stSidebar"] > div {{
    background-color: #EFEFEF !important;
}}

.main {{
    background-color: #F8F8F8 !important;
}}

.main .block-container {{
    padding: 0 !important;
    max-width: 100% !important;
    background-color: #F8F8F8 !important;
}}

/* 전체 채팅 컨테이너 */
.chat-wrapper {{
    position: fixed;
    top: 0;
    left: 300px;
    right: 0;
    bottom: 80px;
    background-color: #F8F8F8;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}}

/* 채팅 영역 */
.chat-area {{
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 20px 40px;
    padding-bottom: 20px;
    background-color: #F8F8F8;
}}

/* 날짜 구분선 */
.date-divider {{
    text-align: center;
    color: #6E6E6E;
    font-size: 12px;
    margin: 15px 0;
    opacity: 0.8;
}}

/* 메시지 컨테이너 */
.message-row {{
    display: flex;
    margin-bottom: 8px;
    align-items: flex-end;
}}

.message-row.user {{
    justify-content: flex-end;
}}

.message-row.bot {{
    justify-content: flex-start;
}}

/* 메시지 버블 */
.bubble {{
    padding: 10px 14px;
    border-radius: 16px;
    max-width: 60%;
    font-size: 14px;
    line-height: 1.4;
    word-wrap: break-word;
    position: relative;
}}

.bubble.bot {{
    background: #E6E7EB;
    color: #000000;
}}

.bubble.user {{
    background: #C4E8B5;
    color: #000000;
}}

/* 타임스탬프 */
.timestamp {{
    font-size: 11px;
    color: #6E6E6E;
    margin: 0 8px;
    align-self: flex-end;
}}

/* 입력창 영역 완전히 새로 만들기 */
.input-fixed-bar {{
    position: fixed;
    bottom: 0;
    left: 300px;
    right: 0;
    background-color: #F0F0F0;
    padding: 12px 20px;
    border-top: 1px solid #D0D0D0;
    z-index: 999;
}}

/* Streamlit 컨테이너 숨기기 */
[data-testid="stHorizontalBlock"] {{
    background-color: transparent !important;
}}

/* Streamlit 입력 필드 스타일 */
.stTextInput {{
    margin-bottom: 0 !important;
}}

.stTextInput > div {{
    background-color: transparent !important;
}}

.stTextInput > div > div {{
    background-color: transparent !important;
}}

.stTextInput > div > div > input {{
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #FFFFFF !important;
    border-radius: 20px !important;
    padding: 10px 16px !important;
    font-size: 14px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
}}

.stTextInput > div > div > input::placeholder {{
    color: #808080 !important;
}}

.stTextInput > div > div > input:focus {{
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
}}

/* 버튼 스타일 */
.stButton {{
    margin-bottom: 0 !important;
}}

.stButton > button {{
    background-color: #C4E8B5 !important;
    color: #000000 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
}}

.stButton > button:hover {{
    background-color: #B0D9A0 !important;
}}

/* 스크롤바 스타일 */
.chat-area::-webkit-scrollbar {{
    width: 8px;
}}

.chat-area::-webkit-scrollbar-track {{
    background: transparent;
}}

.chat-area::-webkit-scrollbar-thumb {{
    background: #CCCCCC;
    border-radius: 4px;
}}

.chat-area::-webkit-scrollbar-thumb:hover {{
    background: #AAAAAA;
}}
</style>
"""
st.markdown(css, unsafe_allow_html=True)


###############################################################
# SIDEBAR UI
###############################################################
with st.sidebar:
    st.markdown(
        f"""
        <div style="padding:30px 20px; text-align:center;">
            <div style="width:80px; height:80px; border-radius:50%; 
                        overflow:hidden; margin:0 auto 15px auto;
                        border:2px solid #E0E0E0; background:#FFF;">
                <img src="{img_src}" style="width:100%; height:100%; object-fit:cover;">
            </div>
            <div style="font-size:20px; font-weight:600; color:#000;">Evan AI</div>
            <div style="color:#4CAF50; font-size:13px; margin-top:5px;">● online</div>
            <hr style="margin:25px 0; border:none; border-top:1px solid #E0E0E0;">
            <div style="font-size:14px; color:#666; cursor:pointer;">⚙️ Settings</div>
        </div>
        """,
        unsafe_allow_html=True
    )


###############################################################
# 채팅 영역 렌더링
###############################################################
st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)
st.markdown('<div id="chat-area" class="chat-area">', unsafe_allow_html=True)

# 날짜를 맨 위에 먼저 표시
if st.session_state.messages:
    first_date = datetime.now().strftime("%Y년 %m월 %d일")
    st.markdown(f"<div class='date-divider'>{first_date}</div>", unsafe_allow_html=True)

last_date = first_date if st.session_state.messages else None

for m in st.session_state.messages:
    msg_date = datetime.now().strftime("%Y년 %m월 %d일")
    
    # 날짜는 맨 위에 한 번만 표시하므로 여기서는 체크하지 않음

    role = m["sender"]
    row_class = "message-row user" if role == "user" else "message-row bot"
    bubble_class = "bubble user" if role == "user" else "bubble bot"
    safe_text = html.escape(m["text"])
    timestamp = m["time"]

    if role == "user":
        html_content = f"""
        <div class="{row_class}">
            <div class="timestamp">{timestamp}</div>
            <div class="{bubble_class}">{safe_text}</div>
        </div>
        """
    else:
        html_content = f"""
        <div class="{row_class}">
            <div class="{bubble_class}">{safe_text}</div>
            <div class="timestamp">{timestamp}</div>
        </div>
        """
    
    st.markdown(html_content, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


###############################################################
# 입력창 (하단 고정)
###############################################################
st.markdown('<div class="input-fixed-bar">', unsafe_allow_html=True)

col1, col2 = st.columns([8, 1])

with col1:
    user_input = st.text_input(
        "",
        value=st.session_state.draft,
        placeholder="메시지를 입력하세요",
        label_visibility="collapsed",
        key="input_field"
    )

with col2:
    send_button = st.button("전송", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)


###############################################################
# 자동 스크롤 스크립트
###############################################################
st_html("""
<script>
setTimeout(function() {
    var chatArea = window.parent.document.getElementById("chat-area");
    if (chatArea) {
        chatArea.scrollTop = chatArea.scrollHeight;
    }
}, 100);
</script>
""", height=0)


###############################################################
# 메시지 처리
###############################################################
def now():
    return datetime.now().strftime("%p %I:%M").replace("AM", "오전").replace("PM", "오후")

if send_button and user_input.strip():
    msg = user_input.strip()
    
    # 사용자 메시지 추가
    st.session_state.messages.append({
        "sender": "user",
        "text": msg,
        "time": now()
    })
    
    # 봇 응답 생성
    try:
        reply = get_bot_reply(msg, st.session_state.messages)
    except Exception as e:
        reply = "응답을 생성하는 중 오류가 발생했습니다."
    
    # 봇 메시지 추가
    st.session_state.messages.append({
        "sender": "bot",
        "text": reply,
        "time": now()
    })
    
    # 입력창 초기화
    st.session_state.draft = ""
    st.rerun()