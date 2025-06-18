from flask import Flask
from app.chatbot_system import ChatbotSystem
# from app.integrations.whatsapp_handler import WhatsAppHandler  # WhatsApp 핸들러 제거
# from app.routes.webhook_routes import webhook_bp  # WhatsApp webhook 라우트 제거
from app.routes.dashboard_routes import dashboard_bp
from app.routes.other_routes import other_bp
from app.routes.chat_routes import chat_bp  # 새로운 채팅 라우트 추가
import os
import logging

def create_app():
    """Flask 앱 생성 및 설정 (로컬 테스트 모드)"""
    app = Flask(__name__)
    
    # 시스템 초기화 (WhatsApp 핸들러 없이)
    chatbot_system = ChatbotSystem()
    
    # 데이터 로드
    excel_file_path = "data/GodQuestions_raw_Kor_2025-04-29.xlsx"
    if os.path.exists(excel_file_path):
        chatbot_system.load_qa_dataset(excel_file_path)
        logging.info(f"✅ QnA dataset loaded from {excel_file_path}")
    else:
        logging.warning(f"⚠️ QnA data file not found at {excel_file_path}")

    # 챗봇 시스템만 등록 (WhatsApp 핸들러 제거)
    app.config['CHATBOT_SYSTEM'] = chatbot_system
    # app.config['WHATSAPP_HANDLER'] = whatsapp_handler  # 제거

    # 블루프린트 등록 (webhook 제외, chat 추가)
    # app.register_blueprint(webhook_bp)  # WhatsApp webhook 라우트 제거
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(other_bp)
    app.register_blueprint(chat_bp)  # 새로운 채팅 인터페이스 추가
    
    logging.info("🔧 Flask app created in local testing mode")
    logging.info("💬 Chat interface available at /chat")
    
    return app