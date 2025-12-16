import traceback
import sys
try:
    import pysqlite3
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    import sqlite3

from datetime import datetime
import html
import streamlit as st
from streamlit.components.v1 import html as st_html
import base64


###############################################################
# BOT LOADING (디버깅 버전)
###############################################################
try:
    from bot_adapter import get_bot_reply, load_bot_once
    load_bot_once()
    st.sidebar.success("✅ Bot loaded successfully!")
except Exception as e:
    # ⚠️ 에러 상세 정보 출력
    st.sidebar.error(f"❌ Bot loading failed!")
    st.sidebar.error(f"Error: {str(e)}")
    st.sidebar.code(traceback.format_exc())
    
    # Fallback 함수
    def get_bot_reply(message, history):
        return f"(demo) {message}"


###############################################################
# STREAMLIT PAGE CONFIG
###############################################################
st.set_page_config(
    page_title="Evan AI Chat",
    page_icon="💬",
    layout="wide",
)


###############################################################
# 이미지 로드
###############################################################
def get_image_base64(image_path):
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

if "input_field" not in st.session_state:
    st.session_state.input_field = ""


###############################################################
# CSS
###############################################################
img_base64 = get_image_base64("bible.png")
img_src = f"data:image/png;base64,{img_base64}" if img_base64 else "https://via.placeholder.com/90"

st.markdown("""
<style>
/* 전체 배경 */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
.main,
.main .block-container {
    background-color: #F2F3F5 !important;
    margin: 0;
    padding: 0;
}

/* 헤더 제거 */
[data-testid="stHeader"],
[data-testid="stToolbar"] {
    display: none !important;
}

/* 사이드바 */
section[data-testid="stSidebar"] {
    background-color: #ECECEC !important;
}

/* 채팅 레이아웃 */
.chat-wrapper {
    position: fixed;
    top: 0;
    left: 300px;
    right: 0;
    bottom: 80px;
    display: flex;
    flex-direction: column;
    background-color: #F2F3F5;
}

.chat-area {
    flex: 1;
    overflow-y: auto;
    padding: 20px 40px;
    background-color: #F2F3F5;
}

/* 메시지 */
.message-row {
    display: flex;
    margin-bottom: 8px;
}

.message-row.user { justify-content: flex-end; }
.message-row.bot { justify-content: flex-start; }

.bubble {
    padding: 10px 14px;
    border-radius: 16px;
    max-width: 60%;
    font-size: 14px;
    color: #1f1f1f;
}

/* 말풍선 색 */
.bubble.user { background: #BEE3AF; }
.bubble.bot { background: #E1E3E8; }

/* 타임스탬프 */
.timestamp {
    font-size: 11px;
    color: #6E6E6E;
    margin: 0 8px;
    align-self: flex-end;
}

/* 입력 바 */
.input-fixed-bar {
    position: fixed;
    bottom: 0;
    left: 300px;
    right: 0;
    background-color: #E9EAEC;
    padding: 12px 20px;
    border-top: 1px solid #D0D0D0;
}
</style>
""", unsafe_allow_html=True)


###############################################################
# SIDEBAR
###############################################################
with st.sidebar:
    st.markdown(f"""
    <div style="padding:30px 20px; text-align:center;">
        <div style="width:80px; height:80px; border-radius:50%;
                    overflow:hidden; margin:0 auto 15px auto;">
            <img src="{img_src}" style="width:100%; height:100%; object-fit:cover;">
        </div>
        <div style="font-size:20px; font-weight:600;">Evan AI</div>
        <div style="color:#4CAF50; font-size:13px;">● online</div>
    </div>
    """, unsafe_allow_html=True)


###############################################################
# 채팅 렌더링
###############################################################
st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)
st.markdown('<div id="chat-area" class="chat-area">', unsafe_allow_html=True)

today = datetime.now().strftime("%Y년 %m월 %d일")
st.markdown(
    f"<div style='text-align:center;color:#777;font-size:12px;'>{today}</div>",
    unsafe_allow_html=True
)

for m in st.session_state.messages:
    role = m["sender"]
    safe_text = html.escape(m["text"])
    timestamp = m["time"]

    if role == "user":
        html_content = f"""
        <div class="message-row user">
            <div class="timestamp">{timestamp}</div>
            <div class="bubble user">{safe_text}</div>
        </div>
        """
    else:
        html_content = f"""
        <div class="message-row bot">
            <div class="bubble bot">{safe_text}</div>
            <div class="timestamp">{timestamp}</div>
        </div>
        """

    st.markdown(html_content, unsafe_allow_html=True)

st.markdown("</div></div>", unsafe_allow_html=True)


###############################################################
# 자동 스크롤
###############################################################
st_html("""
<script>
setTimeout(() => {
    const chat = window.parent.document.getElementById("chat-area");
    if (chat) chat.scrollTop = chat.scrollHeight;
}, 100);
</script>
""", height=0)


###############################################################
# 메시지 전송 함수
###############################################################
def now():
    return datetime.now().strftime("%p %I:%M").replace("AM", "오전").replace("PM", "오후")


def send_message():
    msg = st.session_state.input_field.strip()
    if not msg:
        return

    st.session_state.messages.append({
        "sender": "user",
        "text": msg,
        "time": now()
    })

    st.session_state.input_field = ""

    with st.spinner("Evan AI가 답변 중입니다..."):
        try:
            reply = get_bot_reply(msg, st.session_state.messages)
        except Exception as e:
            reply = f"응답 생성 중 오류가 발생했습니다: {str(e)}"

    st.session_state.messages.append({
        "sender": "bot",
        "text": reply,
        "time": now()
    })

    st.rerun()


###############################################################
# 입력창
###############################################################
st.markdown('<div class="input-fixed-bar">', unsafe_allow_html=True)

col1, col2 = st.columns([8, 1])

with col1:
    st.text_input(
        "",
        key="input_field",
        placeholder="메시지를 입력하세요",
        label_visibility="collapsed",
        on_change=send_message
    )

with col2:
    if st.button("전송", use_container_width=True):
        send_message()

st.markdown("</div>", unsafe_allow_html=True)