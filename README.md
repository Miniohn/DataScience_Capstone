# Digital Mission AI Chatbot (Last Call 프로젝트)

본 프로젝트는 디지털 선교 현장에서의 인력 부족 문제, 응답 지연, 정서적 소진, 악성 사용자 대응 문제 등을 해결하기 위해 개발된 AI 기반 전도 챗봇 시스템입니다. 특히 연간 30,000명 이상의 신규 유입자를 10~20명의 사역자가 감당해야 하는 Last Call 플랫폼의 실제 문제를 해결하기 위한 실무형 AI 솔루션으로 설계되었습니다.

---

### 프로젝트 주요 기능

- **Adaptive RAG 기반 AI 응답 시스템**
- **Router / Block / Default / RAG 에이전트 구조**
- **신학적 정확도 확보를 위한 RAG 기반 답변 생성**
- **욕설·악성 사용자 자동 필터링**
- **초기 응답 자동화 (평균 347.8분 → 30초 이하)**
- **Streamlit 기반 챗봇 UI**
- **MongoDB 기반 로그 저장 및 분석**
- **Golden Dataset + RAGAS 평가를 통한 모델 지속 개선**

---

### 프로젝트 구조

```
Chatbot_ver2/
 ├── streamlit/                # Streamlit 웹 앱 파일
 │     ├── app.py              # 메인 실행 파일
 │     ├── chatbot_revised.ipynb
 │     ├── demo.py
 │     └── revised.py
 │
 ├── data/                     # 원본 데이터
 │     ├── whatsapp/
 │     ├── gq/
 │     └── book/
 │
 ├── data_preprocessing/
 │     └── preprocessing.ipynb # 메시지 정제 파이프라인
 │
 ├── evaluation/               # RAGAS 및 모델 평가
 │     ├── chatbot_for_evaluation.ipynb
 │     ├── evaluation_with_ragas.ipynb
 │     ├── finaltest_with_ragas.ipynb
 │     └── GQ_summary_with_ai.ipynb
 │
 ├── requirements.txt
 └── README.md
```

---

### 기술 스택 (Tech Stack)

- Python 3.11  
- Upstage LLM (Solar API)  
- LangChain / LangGraph  
- ChromaDB (벡터 스토어)  
- Streamlit  
- MongoDB  
- pandas, pydantic, dotenv  

---

### 환경 변수 (.env 설정)

프로젝트 루트에 `.env` 파일을 생성하고 아래 내용을 작성합니다:

```
UPSTAGE_API_KEY=up_xxxxxx
MONGO_IP=127.xx.xx.xx
MONGO_PORT=27017
MONGO_USER=your_username
MONGO_PASSWORD=your_password
```

⚠️ **API Key와 DB 정보는 GitHub에 절대 노출하지 마세요.**

---

### 실행 방법 (Run App)

1. 저장소 클론  
```
git clone https://github.com/yourname/Chatbot_ver2.git
cd Chatbot_ver2
```

2. 필요한 라이브러리 설치  
```
pip install -r requirements.txt
```

3. Streamlit 앱 실행  
```
cd streamlit
streamlit run app.py
```

브라우저가 자동으로 열리며 챗봇이 실행됩니다.

---

### LLM 엔진 교체 방법 (Upstage → 다른 모델)

본 프로젝트는 기본적으로 **Upstage Solar LLM** 기반으로 설계되어 있지만,  
LangChain의 ChatModel 부분만 변경하면  
OpenAI · Claude · Gemini · Local LLM(Ollama 등)으로 교체할 수 있습니다.

#### 현재 Upstage 사용:
```python
from langchain_upstage import ChatUpstage

llm = ChatUpstage(
    api_key=os.getenv("UPSTAGE_API_KEY"),
    model="solar-1-mini-chat"
)
```

#### OpenAI로 바꾸고 싶다면?
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)
```

#### 로컬 LLM(Ollama 등)을 쓰고 싶다면?
```python
from langchain_community.chat_models import ChatOllama

llm = ChatOllama(model="llama3")
```

즉, **LLM 교체는 1줄만 바꾸면 가능하도록 구조화**되어 있습니다.

---

### 데이터 및 평가

- WhatsApp 실제 대화 3,017건  
- Got Questions 크롤링 데이터 2,175개  
- 기독교 변증학 서적 기반 Q&A 약 1,000개  
- 선교사 직접 검수 Golden Dataset 150개  

**평가 지표 (RAGAS 기반)**  
- Correctness  
- Semantic Similarity  
- Relevancy  
