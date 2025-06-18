# app/routes/chat_routes.py
from flask import Blueprint, render_template_string, request, jsonify, current_app
import logging

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat')
def chat_page():
    """AI와 대화할 수 있는 웹 채팅 인터페이스"""
    return render_template_string("""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 AI 상담 채팅</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .chat-container {
            width: 90%;
            max-width: 800px;
            height: 80vh;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .chat-header {
            background: #25D366;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
        }
        .message {
            margin-bottom: 15px;
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
        }
        .user-message {
            background: #007bff;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .ai-message {
            background: white;
            color: #333;
            border: 1px solid #e9ecef;
            margin-right: auto;
        }
        .chat-input {
            display: flex;
            padding: 20px;
            background: white;
            border-top: 1px solid #e9ecef;
        }
        .chat-input input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #ddd;
            border-radius: 25px;
            outline: none;
            font-size: 16px;
        }
        .chat-input button {
            margin-left: 10px;
            padding: 12px 24px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
        }
        .chat-input button:hover {
            background: #0056b3;
        }
        .chat-input button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 10px;
            color: #666;
        }
        .typing {
            display: none;
            background: white;
            color: #666;
            margin-right: auto;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🤖 AI 상담 채팅</h1>
            <p>궁금한 것이 있으면 언제든 물어보세요!</p>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="message ai-message">
                안녕하세요! 저는 AI 상담사입니다. 어떤 도움이 필요하신가요? 😊
            </div>
        </div>
        
        <div class="loading" id="loading">
            AI가 답변을 생각하고 있습니다...
        </div>
        
        <div class="chat-input">
            <input type="text" id="messageInput" placeholder="메시지를 입력하세요..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()" id="sendButton">전송</button>
        </div>
    </div>

    <script>
        const chatMessages = document.getElementById('chatMessages');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const loading = document.getElementById('loading');

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;

            // 사용자 메시지 추가
            addMessage(message, 'user');
            messageInput.value = '';
            
            // 로딩 상태 표시
            setLoading(true);

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });

                const data = await response.json();
                
                if (data.success) {
                    addMessage(data.response, 'ai');
                } else {
                    addMessage('죄송합니다. 오류가 발생했습니다: ' + data.error, 'ai');
                }
            } catch (error) {
                addMessage('죄송합니다. 서버 연결에 문제가 있습니다.', 'ai');
                console.error('Error:', error);
            }
            
            setLoading(false);
        }

        function addMessage(text, sender) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.textContent = text;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function setLoading(isLoading) {
            loading.style.display = isLoading ? 'block' : 'none';
            sendButton.disabled = isLoading;
            sendButton.textContent = isLoading ? '전송 중...' : '전송';
        }

        // 페이지 로드 시 입력창에 포커스
        messageInput.focus();
    </script>
</body>
</html>
    """)

@chat_bp.route('/api/chat', methods=['POST'])
def api_chat():
    """AI와의 채팅 API 엔드포인트"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': '메시지가 비어있습니다.'
            })

        # 챗봇 시스템에서 응답 생성
        chatbot_system = current_app.config['CHATBOT_SYSTEM']
        
        # 임시 사용자 ID (실제로는 세션 관리가 필요)
        user_id = "web_user_" + request.remote_addr.replace('.', '_')
        
        # AI 응답 생성
        ai_response = chatbot_system.process_message(user_id, user_message)
        
        # 응답이 객체인 경우 문자열로 변환
        if isinstance(ai_response, dict):
            # 딕셔너리에서 응답 텍스트 추출
            response_text = ai_response.get('response', str(ai_response))
        elif hasattr(ai_response, 'content'):
            # 객체에 content 속성이 있는 경우
            response_text = ai_response.content
        elif hasattr(ai_response, 'text'):
            # 객체에 text 속성이 있는 경우
            response_text = ai_response.text
        else:
            # 그 외의 경우 문자열로 변환
            response_text = str(ai_response)
        
        return jsonify({
            'success': True,
            'response': response_text,
            'user_message': user_message
        })
        
    except Exception as e:
        logging.error(f"Chat API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': '서버에서 오류가 발생했습니다.'
        })