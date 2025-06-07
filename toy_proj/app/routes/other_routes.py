# app/routes/other_routes.py
from flask import Blueprint, jsonify, current_app
from datetime import datetime

# 1. 'other_bp'라는 이름으로 새로운 Blueprint 생성
other_bp = Blueprint('other', __name__)

@other_bp.route('/health')
def health_check():
    """시스템의 상태를 확인하는 헬스 체크 엔드포인트입니다."""
    
    # 2. 'chatbot_system'을 current_app.config에서 가져오도록 수정
    try:
        chatbot_system = current_app.config['CHATBOT_SYSTEM']
        active_handoff_count = len(chatbot_system.active_handoffs)
        total_session_count = len(chatbot_system.sessions)
    except KeyError:
        # chatbot_system이 초기화되지 않은 경우 대비
        active_handoff_count = "N/A"
        total_session_count = "N/A"

    return jsonify({
        "status": "healthy",
        "system": "Multi-Agent Counseling + WhatsApp",
        "timestamp": datetime.now().isoformat(),
        "active_handoffs": active_handoff_count,
        "total_sessions": total_session_count
    })

@other_bp.route('/test')
def test_page():
    """기능 테스트를 위한 안내 페이지를 보여줍니다."""
    return """
    <html>
    <head>
        <title>🧪 Test System</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; margin: 40px; line-height: 1.6; }
            h1, h3 { color: #333; }
            ul { list-style-type: none; padding-left: 0; }
            li { background: #f4f4f4; margin-bottom: 8px; padding: 10px; border-radius: 5px; }
            code { background: #e1e1e1; padding: 2px 5px; border-radius: 3px; }
            a { color: #007bff; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>🧪 Test Multi-Agent Counseling System</h1>
        
        <h3>📱 Test Messages (to AI):</h3>
        <p><strong>Basic Questions (AI should handle):</strong></p>
        <ul>
            <li>"What does the Bible say about love?"</li>
            <li>"How should I pray?"</li>
            <li>"I'm feeling sad today"</li>
        </ul>
        
        <p><strong>Complex/Sensitive Topics (may trigger handoff):</strong></p>
        <ul>
            <li>"What's the difference between Calvinism and Arminianism?"</li>
            <li>"How do we reconcile God's sovereignty with free will?"</li>
            <li>"I am having suicidal thoughts"</li>
        </ul>
        
        <h3>👨‍💼 Counselor Commands (via WhatsApp):</h3>
        <ul>
            <li><code>ACCEPT [session_id]</code> - Accept and take over the case.</li>
            <li><code>INFO [session_id]</code> - Get full conversation history.</li>
            <li><code>BUSY</code> - Mark yourself as unavailable for new handoffs.</li>
        </ul>
        
        <h3>🔗 Quick Links:</h3>
        <ul>
            <li><a href="/dashboard">📊 Dashboard</a></li>
            <li><a href="/health">❤️ Health Check</a></li>
        </ul>
    </body>
    </html>
    """