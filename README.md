# Chatbot_ver2

**AI로 디지털 선교의 "첫 응답"을 맡기다**

이 프로젝트는 **디지털 선교 현장에서 반복되는 인력 부족과 응답 지연 문제**를 해결하기 위해 만들어진 **AI 기반 전도·상담 보조 챗봇**입니다.

연간 약 **3만 명**이 유입되는 디지털 선교 플랫폼에서, 이를 감당하는 사역자는 고작 **10–20명**. 질문 하나에 몇 시간씩 기다려야 하는 상황은 흔하고, 사역자들은 단순 인사부터 공격적인 메시지까지 모든 대화를 직접 감당해야 합니다.

**Chatbot_ver2는 이 "첫 응답"을 AI에게 맡깁니다.**

<br>

---

## 💡 What this project does

### 🙋‍♂️ 초기 응대 자동화
인사, 반복 질문, 기본적인 신앙 질문을 즉시 대응합니다.

### 🚫 악성·공격적 메시지 필터링
욕설, 광고, 반기독교적 공격 메시지를 자동으로 차단합니다.

### 📖 신학적으로 검증된 답변 제공
Got Questions, 기독교 변증학 자료, 실제 선교 데이터 기반으로 환각을 최소화한 RAG 응답을 생성합니다.

### 🤝 사역자를 돕는 챗봇
AI가 모든 것을 대신하는 것이 아니라, 사람이 꼭 필요한 순간에만 사역자가 개입하도록 설계되었습니다.

<br>

---

## 🎯 Why it matters

실제 데이터 분석 결과, 사용자가 메시지를 보낸 뒤 사역자가 응답하기까지 평균 **347.8분(약 6시간)**이 걸리고 있었습니다.

이 프로젝트는 그 시간을 **30초 이내**로 줄이는 것을 목표로 합니다.

**그 결과:**
- 사역자는 감정 소모가 큰 대화에서 보호받고
- 더 많은 사람에게 더 빠르게 응답할 수 있으며
- 디지털 선교 플랫폼은 지속 가능한 구조를 갖게 됩니다

<br>

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| **LLM** | Upstage Solar Pro |
| **Framework** | LangGraph |
| **Vector DB** | ChromaDB |
| **Retrieval** | BM25 + Vector Search (Ensemble) |
| **UI** | Streamlit |
| **Evaluation** | RAGAS |
| **Language** | Python 3.10+ |

<br>

---

## 🚀 Quick Start

### 환경 변수 설정

프로젝트 루트의 `Chatbot_ver2` 폴더 안에 `.env` 파일을 생성하고 아래 내용을 입력하세요.

```env
# .env example
UPSTAGE_API_KEY="sk-..."          # Upstage API 키
MONGODB_URI="mongodb+srv://..."   # MongoDB 접속 주소 (선택사항)
DB_NAME="chat_db"                 # 데이터베이스 이름 (선택사항)
COLLECTION_NAME="chat_logs"       # 컬렉션 이름 (선택사항)
```

> **참고:** MongoDB 설정 없이도 챗봇은 정상 작동합니다. MongoDB는 로그 저장용입니다.

<br>

### 사전 요구사항

**필수 소프트웨어:**
- Python 3.10 이상
- 인터넷 연결 (패키지 다운로드용)

**Python 설치 확인:**
```bash
python --version
# 또는
python3 --version
```

출력 예시: `Python 3.10.11`

<br>

### 설치 가이드

<details>
<summary><b>🪟 Windows 설치 가이드</b></summary>

<br>

#### 1단계: 프로젝트 폴더로 이동

**명령 프롬프트(CMD) 실행:**
- `Windows 키 + R` → `cmd` 입력 → Enter
- 또는 검색창에서 "명령 프롬프트" 검색

**프로젝트 폴더로 이동:**
```cmd
cd C:\Users\Desktop\DataScience_Capstone
```

<br>

#### 2단계: 가상환경 생성

```cmd
python -m venv venv
```

> **참고:** `venv`는 가상환경 폴더 이름입니다.

<br>

#### 3단계: 가상환경 활성화

```cmd
venv\Scripts\activate.bat
```

**성공 확인:** 프롬프트 앞에 `(venv)`가 표시됩니다.
```
(venv) C:\Users\Desktop\DataScience_Capstone>
```

<br>

#### 4단계: pip 업그레이드

```cmd
python -m pip install --upgrade pip
```

<br>

#### 5단계: 패키지 설치

```cmd
pip install -r requirements.txt
```

**설치 시간:** 약 5-10분 소요

<br>

#### 6단계: Streamlit 앱 실행

```cmd
cd Chatbot_ver2\streamlit
streamlit run app.py
```

**실행 확인:** 브라우저가 자동으로 열리고 `http://localhost:8501`에서 앱이 실행됩니다.

<br>

#### 가상환경 비활성화 (종료 시)

```cmd
deactivate
```

</details>

<br>

<details>
<summary><b>🍎 macOS 설치 가이드</b></summary>

<br>

#### 1단계: 프로젝트 폴더로 이동

**터미널 실행:**
- `Command + Space` → "터미널" 입력 → Enter
- 또는 응용 프로그램 > 유틸리티 > 터미널

**프로젝트 폴더로 이동:**
```bash
cd ~/Desktop/DataScience_Capstone
```

<br>

#### 2단계: 가상환경 생성

```bash
python3 -m venv venv
```

> **참고:** macOS에서는 `python3` 명령어를 사용합니다.

<br>

#### 3단계: 가상환경 활성화

```bash
source venv/bin/activate
```

**성공 확인:** 프롬프트 앞에 `(venv)`가 표시됩니다.
```
(venv) username@MacBook-Pro DataScience_Capstone %
```

<br>

#### 4단계: pip 업그레이드

```bash
python -m pip install --upgrade pip
```

<br>

#### 5단계: 패키지 설치

```bash
pip install -r requirements.txt
```

**설치 시간:** 약 5-10분 소요

<br>

#### 6단계: Streamlit 앱 실행

```bash
cd Chatbot_ver2/streamlit
streamlit run app.py
```

**실행 확인:** 브라우저가 자동으로 열리고 `http://localhost:8501`에서 앱이 실행됩니다.

<br>

#### 가상환경 비활성화 (종료 시)

```bash
deactivate
```

</details>

<br>

<details>
<summary><b>⚡ 다음 실행부터는 (빠른 시작)</b></summary>

<br>

**Windows:**
```cmd
cd C:\Users\Desktop\DataScience_Capstone
venv\Scripts\activate.bat
cd Chatbot_ver2\streamlit
streamlit run app.py
```

<br>

**macOS:**
```bash
cd ~/Desktop/DataScience_Capstone
source venv/bin/activate
cd Chatbot_ver2/streamlit
streamlit run app.py
```

</details>

<br>

---

## 📁 프로젝트 구조

```
DataScience_Capstone/
├── Chatbot_ver2/                     # 메인 프로젝트
│   ├── chatbot_with_MongoDB.ipynb    # 핵심 챗봇 로직
│   ├── demo1.py                      # CLI 실행용 스크립트
│   ├── data/                         # 지식베이스 데이터
│   │   ├── book/                     # 사역서적 (영문 변환)
│   │   ├── gq/                       # Got Questions QnA
│   │   └── golden_dataset/           # RAGAS 검증 완료 데이터
│   ├── chroma_db/                    # 벡터 DB (자동 생성)
│   └── streamlit/                    # 웹 UI
│       ├── app.py                    # Streamlit 앱
│       ├── bot_adapter.py            # 챗봇 연결 어댑터
│       └── bible.png                 # 프로필 이미지
│
├── GotQuestions_Crawling_code/       # GQ 데이터 수집
├── evaluation/                       # RAGAS 평가 파이프라인
├── puppeteer_whatsappcrawling/       # WhatsApp 대화 수집
├── requirements.txt
└── README.md
```

<br>

---

## 📂 폴더별 상세 설명

<details>
<summary><b>📦 Chatbot_ver2/ - 메인 프로젝트</b></summary>

<br>

### 🗂️ data/ - 지식베이스 & 평가 데이터

챗봇이 참고하는 **원문 지식**과 **검증된 QnA 데이터셋**을 저장합니다.

| 폴더 | 설명 |
|------|------|
| `data/book/` | 사역 현장에서 사용하는 책 13권을 영어로 번역한 텍스트 |
| `data/gq/` | Got Questions에서 수집한 QnA 원본 데이터 |
| `data/golden_dataset/` | RAGAS로 평가 완료된 검증된 QnA 데이터 |

<br>

### 🖥️ streamlit/ - 웹 UI

사용자가 바로 사용할 수 있는 채팅 인터페이스를 제공합니다.

| 파일 | 설명 |
|------|------|
| `app.py` | Streamlit 채팅 화면 구성 및 메시지 처리 |
| `bot_adapter.py` | UI와 챗봇 로직을 연결하는 어댑터 |
| `bible.png` | 프로필 이미지 |

<br>

### 🧠 chatbot_with_MongoDB.ipynb - 핵심 로직

**메인 챗봇 로직이 모두 들어있는 핵심 파일입니다.**

**주요 구성요소:**

1. **모델 & 상태 관리**
   - Upstage Solar Pro LLM 설정
   - TypedDict 기반 State 관리

2. **데이터 로딩 & 벡터DB**
   - ChromaDB 기반 벡터 스토어 구축
   - BM25 + Vector Search 하이브리드 검색

3. **번역 시스템**
   - 페르시아어 ↔ 영어 자동 번역
   - 다국어 지원 인프라

4. **지능형 라우팅**
   - RAG: 신앙 질문 (근거 기반 답변)
   - Default: 일반 대화
   - Block: 악성 메시지 차단
   - Handoff: 사람 상담원 연결

5. **RAG 파이프라인**
   - 검색 결과 품질 판단
   - 답변 생성
   - 쿼리 재작성 (검색 개선)

6. **MongoDB 로깅**
   - 대화별/단계별 로그 저장
   - 품질 개선을 위한 데이터 수집

</details>

<br>

<details>
<summary><b>🕸️ GotQuestions_Crawling_code/ - 데이터 수집</b></summary>

<br>

**Got Questions 웹사이트에서 QnA 데이터를 수집하는 크롤링 코드입니다.**

### 📂 파일 구성

| 파일 | 설명 |
|------|------|
| `GotQuestion_Crawling_Kor.ipynb` | 한국어 Got Questions 크롤링 |
| `GotQuestions_Crawling_Far.ipynb` | 페르시아어 Got Questions 크롤링 |
| `GotQuestion_Crawling_Arabic.ipynb` | 아랍어 Got Questions 크롤링 |

<br>

### 🛠️ 크롤링 방식

1. 질문 목록 페이지 수집
2. 개별 질문 페이지 접근
3. 질문 제목 + 답변 본문 파싱
4. QnA 형태로 정리 → `data/gq/`로 이동

<br>

### 💡 왜 언어별로 분리?

Got Questions는 **언어마다 페이지 구조가 다르기 때문**에 언어별 노트북으로 분리하여 유지보수성을 높였습니다.

</details>

<br>

<details>
<summary><b>🧪 evaluation/ - Golden Dataset 제작 & 품질 평가</b></summary>

<br>

**QnA를 만들고 → RAGAS로 평가하고 → 개선하는 실험실입니다.**

<br>

### ✅ 전체 워크플로우

1. **GQ 답변 요약** (채팅용으로 짧게 변환)
2. **요약 후보 3개 생성 → RAGAS로 베스트 선택**
3. **Golden Dataset vs 챗봇 답변 비교 평가**

<br>

### 📝 주요 노트북

**1) GQ_summary_with_ai.ipynb**
- Got Questions 답변을 2-4문장으로 요약
- TF-IDF 유사도로 품질 검증
- `GQ_Summarized_Full.xlsx` 생성

<br>

**2) evaluation_with_ragas.ipynb** ⭐ 핵심
- 요약 후보 3개 생성
- RAGAS 지표로 평가 (Relevancy, Correctness, Similarity)
- 가중치 기반 Best Summary 선택
- 10개 단위 중간 저장 + Resume 로직

<br>

**3) finaltest_with_ragas.ipynb**
- Golden Dataset(모범답안) vs 챗봇 답변 비교
- Answer Similarity & Correctness 평가
- 점수 낮은 케이스 분석 → 개선 포인트 도출

<br>

**4) chatbot_for_evaluation.ipynb**
- 평가용 챗봇 답변 생성 보조 노트북

</details>

<br>

<details>
<summary><b>📱 puppeteer_whatsappcrawling/ - 현장 대화 수집</b></summary>

<br>

**Puppeteer로 WhatsApp Web에서 실제 사역 대화를 수집합니다.**

<br>

### 📂 폴더 구성

| 항목 | 설명 |
|------|------|
| `whatsapp_crawling_puppeteer.js` | 메인 크롤러 스크립트 |
| `myUserDataDirWhatsApp/` | Chrome 세션 유지용 |
| `whatsapp_exports/` | 채팅방별 `.txt` 저장 |
| `package.json` | Node.js 환경 설정 |

<br>

### 🛠️ 크롤링 방식

1. **WhatsApp Web 자동 접속**
   - QR 코드 최초 1회 수동 로그인
   - userDataDir로 세션 유지

2. **채팅 목록 수집**
   - 자동 스크롤로 모든 채팅방 로드
   - 채팅 이름 추출

3. **메시지 추출**
   - 각 채팅방 클릭 → 맨 위까지 스크롤
   - 발신자, 시간, 메시지 텍스트 수집

4. **텍스트 저장**
   - 채팅방당 1개 `.txt` 파일
   - `all_chats_combined.txt` 통합 파일 생성

<br>

### 💡 왜 Puppeteer?

WhatsApp 공식 API는 과거 대화 전체 수집이 제한적이므로, **브라우저 자동화가 가장 현실적인 방법**이었습니다.

덕분에 **가공되지 않은 현장 그대로의 대화 데이터**를 확보할 수 있었습니다.

</details>

<br>

---

## 🎓 Credits & License

### 팀원
- **개발**: 김민제, 심다영, 오하경
- **프로젝트 기간**: 2025.03 - 2026.01

<br>

---

**Last Updated**: 2026-01-24
