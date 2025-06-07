# 필수 라이브러리 임포트
import openai
import os
from dotenv import load_dotenv
import logging
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# 로깅 설정
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 열거형 정의
class AgentType(Enum):
    BLOCK = "BLOCK"
    COUNSELING = "COUNSELING"
    GOSPEL = "GOSPEL"

# 데이터 클래스 정의
@dataclass
class Message:
    content: str
    agent_type: Optional[AgentType] = None
    timestamp: Optional[str] = None
    metadata: Optional[Dict] = None

@dataclass
class QnAData:
    question: str
    answer: str
    category: Optional[str] = None
