from flask import Blueprint, current_app

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def show_dashboard():
    """통합 대시보드 페이지를 렌더링합니다."""
    
    # 3. current_app을 통해 chatbot_system 객체를 안전하게 가져옵니다.
    try:
        chatbot_system = current_app.config['CHATBOT_SYSTEM']
        active_handoffs = chatbot_system.active_handoffs
        total_sessions = len(chatbot_system.sessions)
    except KeyError:
        # 앱이 올바르게 설정되지 않았을 경우의 예외 처리
        return "Error: Chatbot system not initialized correctly.", 500

    handoff_list = ""
    for session_id, handoff_request in active_handoffs.items():
        handoff_list += f"""
        <li style="margin-bottom: 15px; padding: 15px; background-color: #f9f9f9; border-radius: 8px;">
            <div><strong>📱 User:</strong> {handoff_request.user_phone}</div>
            <div><strong>🙏 Urgency:</strong> {handoff_request.urgency.value}</div>
            <div><strong>📋 Reason:</strong> {handoff_request.reason}</div>
            <div><strong>💬 Message:</strong> "{handoff_request.user_message[:100]}..."</div>
            <div><strong>⏰ Time:</strong> {handoff_request.timestamp}</div>
        </li>
        """
    
    # HTML 템플릿 반환
    return f"""
    <html>
    <head>
        <title>🕊️ Counseling Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
            .header {{ background: #25D366; color: white; padding: 20px; text-align: center; border-radius: 8px; }}
            .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
            .stat-box {{ background: white; padding: 20px; border-radius: 8px; text-align: center; flex: 1; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .handoff-section {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            ul {{ list-style: none; padding: 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🕊️ Multi-Agent Counseling System</h1>
            <p>AI-Powered Pastoral Care with WhatsApp Integration</p>
        </div>
        
        <div class="stats">
            <div class="stat-box">
                <h2>{len(active_handoffs)}</h2>
                <p>🙏 Active Handoffs</p>
            </div>
            <div class="stat-box">
                <h2>{total_sessions}</h2>
                <p>💬 Total Sessions</p>
            </div>
            <div class="stat-box">
                <h2>5</h2>
                <p>🤖 AI Agents</p>
            </div>
        </div>
        
        <div class="handoff-section">
            <h2>🙏 Pending Handoff Requests</h2>
            {"<p>No pending handoffs at the moment.</p>" if not active_handoffs else f"<ul>{handoff_list}</ul>"}
        </div>
    </body>
    </html>
    """