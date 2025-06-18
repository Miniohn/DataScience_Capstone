import os
import json
import numpy as np
import pandas as pd
from typing import List, Dict, Any
import google.generativeai as genai # pip install google.generativeai
import pickle

# ========================
# 설정 부분 - 사용자가 수정해야 하는 부분
# ========================

# Google Gemini API 키 설정 (환경변수 또는 직접 입력)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 데이터셋 파일 경로 (사용자가 변경)
DATA_FILE_PATH = "/Users/haley/Desktop/2025-1/DS1/code/need_preprocessing/GodQuestions/GodQuestions_raw_Kor_2025-04-29.xlsx"  # 엑셀 파일 경로

# 임베딩 모델 설정
EMBEDDING_MODEL = "models/embedding-001"  # 구글 임베딩 모델

# 생성 모델 설정
GENERATION_MODEL = "gemini-1.5-flash"  # 또는 gemini-1.5-pro

# 벡터 데이터베이스 저장 파일
VECTOR_DB_FILE = "gemini_vector_database.pkl"

# ========================
# API 연결 테스트 함수
# ========================

def test_gemini_api_connection(api_key: str) -> bool:
    """
    Gemini API 연결 테스트 함수
    간단한 텍스트 생성 요청으로 API 키와 연결 상태 확인
    """
    print("🔍 Gemini API 연결 테스트 중...")
    
    try:
        # API 키 설정
        genai.configure(api_key=api_key)
        
        # 테스트용 모델 생성
        test_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # 간단한 테스트 요청
        test_prompt = "Write a story about a magic backpack."
        response = test_model.generate_content(
            test_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=100  # 테스트이므로 짧게
            )
        )
        
        print("✅ API 연결 성공!")
        print(f"📝 테스트 응답 (처음 100자): {response.text[:100]}...")
        print("-" * 50)
        return True
        
    except Exception as e:
        print("❌ API 연결 실패!")
        print(f"🔴 오류 내용: {e}")
        print("\n🛠️  해결 방법:")
        print("1. GEMINI_API_KEY가 올바르게 설정되었는지 확인")
        print("2. https://makersuite.google.com/app/apikey 에서 유효한 API 키 생성")
        print("3. 인터넷 연결 상태 확인")
        print("4. 환경변수 설정: export GEMINI_API_KEY='your-api-key'")
        print("-" * 50)
        return False