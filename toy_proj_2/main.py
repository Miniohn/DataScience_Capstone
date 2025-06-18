import os
import logging
from dotenv import load_dotenv
from app.flask_app import create_app
from app.utils.excel_loader import create_sample_excel_file

import google.generativeai as genai

# 환경 변수 로드 및 로깅 설정
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Gemini API 키만 확인 (WhatsApp 관련 제거)
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    logging.error("GEMINI_API_KEY is required but not found in environment variables")
    exit(1)

genai.configure(api_key=gemini_api_key)
logging.info("✅ Gemini API configured successfully")

# 샘플 데이터 파일 확인/생성
excel_file_path = "data/GodQuestions_raw_Kor_2025-04-29.xlsx"
if not os.path.exists(excel_file_path):
    logging.info(f"Creating sample Excel file at: {excel_file_path}")
    os.makedirs('data', exist_ok=True)
    create_sample_excel_file(excel_file_path)

# 앱 생성
app = create_app()

if __name__ == "__main__":
    logging.info("🚀 Starting Local AI Counseling System...")
    logging.info("📱 WhatsApp API disabled - Local testing mode")
    logging.info("🌐 Access Dashboard at http://localhost:8000/dashboard")
    logging.info("🧪 Access Test Page at http://localhost:8000/test")
    logging.info("💬 Use the web interface to test AI responses")
    app.run(host='0.0.0.0', port=8000, debug=True)