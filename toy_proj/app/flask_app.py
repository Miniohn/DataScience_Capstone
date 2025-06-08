from flask import Flask
from app.chatbot_system import ChatbotSystem
from app.integrations.whatsapp_handler import WhatsAppHandler
from app.routes.webhook_routes import webhook_bp
from app.routes.dashboard_routes import dashboard_bp
from app.routes.other_routes import other_bp
import os

def create_app():
    """Flask 앱 생성 및 설정"""
    app = Flask(__name__)
    
    # 시스템 초기화
    chatbot_system = ChatbotSystem()
    whatsapp_handler = WhatsAppHandler(chatbot_system)
    
    # 데이터 로드
    excel_file_path = "data/GodQuestions_raw_Kor_2025-04-29.xlsx"
    if os.path.exists(excel_file_path):
        chatbot_system.load_qa_dataset(excel_file_path)
    else:
        print(f"Warning: QnA data file not found at {excel_file_path}")

    # 블루프린트에 핸들러와 시스템 객체 등록 (의존성 주입)
    app.config['CHATBOT_SYSTEM'] = chatbot_system
    app.config['WHATSAPP_HANDLER'] = whatsapp_handler

    # 블루프린트 등록
    app.register_blueprint(webhook_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(other_bp)
    
    return app