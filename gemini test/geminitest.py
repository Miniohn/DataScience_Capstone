import os
from dotenv import load_dotenv
import google.generativeai as genai

# 1. .env 파일에서 환경변수 불러오기
load_dotenv()

# 2. 환경변수에서 API 키 읽기
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("API 키가 환경변수에서 로드되지 않았습니다. .env 파일을 확인하세요.")

# 3. Gemini 모델 구성
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# 4. 사용자 입력 받아 응답 출력
question = input("질문을 입력하세요: ")
response = model.generate_content(question)
print("답변:", response.text)
