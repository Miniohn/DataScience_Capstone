# app/routes/webhook_routes.py
from flask import Blueprint, request, jsonify, current_app

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/webhook/whatsapp', methods=['GET', 'POST'])
def whatsapp_webhook():
    handler = current_app.config['WHATSAPP_HANDLER']
    
    if request.method == 'GET':
        # 웹훅 검증
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if verify_token == handler.verify_token:
            return challenge
        return "Verification failed", 403
    
    elif request.method == 'POST':
        #메시지 처리
        webhook_data = request.get_json()
        
        #상담사 응답인지 ㅎ확인
        message_text = handler._extract_message_text(webhook_data)
        
        #상담사 명령어 처리 
        if message_text.upper().startswith(('ACCEPT', 'INFO', 'BUSY')):
            result = handler.handle_counselor_response(webhook_data)
        else:
            #일반 사용자 메시지 처리
            result = handler.handle_incoming_message(webhook_data)
        
        return jsonify(result)