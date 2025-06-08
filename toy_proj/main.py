import os
import logging
from dotenv import load_dotenv
from app.flask_app import create_app
from app.utils.excel_loader import create_sample_excel_file

import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 환경 변수 로드 및 로깅 설정
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 환경 변수 확인
required_vars = ["GEMINI_API_KEY", "WHATSAPP_ACCESS_TOKEN", "WHATSAPP_PHONE_NUMBER_ID", "WHATSAPP_VERIFY_TOKEN"]
if any(not os.getenv(var) for var in required_vars):
    logging.warning(f"One or more environment variables are missing. The system may not fully function.")

# 샘플 데이터 파일 확인/생성
excel_file_path = "data/GodQuestions_raw_Kor_2025-04-29.xlsx"
if not os.path.exists(excel_file_path):
    logging.info(f"Creating sample Excel file at: {excel_file_path}")
    os.makedirs('data', exist_ok=True)
    create_sample_excel_file(excel_file_path)

# 앱 생성
app = create_app()

if __name__ == "__main__":
    logging.info("🚀 Starting Multi-Agent Counseling System...")
    logging.info("🌐 Access Dashboard at http://localhost:8000/dashboard")
    logging.info("🧪 Access Test Page at http://localhost:8000/test")
    app.run(host='0.0.0.0', port=8000, debug=True)