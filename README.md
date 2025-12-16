# Chatbot_ver2  
AI로 디지털 선교의 “첫 응답”을 맡기다

이 프로젝트는 **디지털 선교 현장에서 반복되는 인력 부족과 응답 지연 문제**를 해결하기 위해 만들어진  
**AI 기반 전도·상담 보조 챗봇**입니다.

연간 약 **3만 명**이 유입되는 디지털 선교 플랫폼에서,  
이를 감당하는 사역자는 고작 **10–20명**.  
질문 하나에 몇 시간씩 기다려야 하는 상황은 흔하고,  
사역자들은 단순 인사부터 공격적인 메시지까지 모든 대화를 직접 감당해야 합니다.

**Chatbot_ver2는 이 “첫 응답”을 AI에게 맡깁니다.**

---

## What this project does

- 🙋‍♂️ **초기 응대 자동화**  
  인사, 반복 질문, 기본적인 신앙 질문을 즉시 대응합니다.

- 🚫 **악성·공격적 메시지 필터링**  
  욕설, 광고, 반기독교적 공격 메시지를 자동으로 차단합니다.

- 📖 **신학적으로 검증된 답변 제공**  
  Got Questions, 기독교 변증학 자료, 실제 선교 데이터 기반으로  
  환각을 최소화한 RAG 응답을 생성합니다.

- 🤝 **사역자를 돕는 챗봇**  
  AI가 모든 것을 대신하는 것이 아니라,  
  사람이 꼭 필요한 순간에만 사역자가 개입하도록 설계되었습니다.

---

## Why it matters

실제 데이터 분석 결과,  
사용자가 메시지를 보낸 뒤 사역자가 응답하기까지 평균 **347.8분(약 6시간)**이 걸리고 있었습니다.

이 프로젝트는 그 시간을 **30초 이내**로 줄이는 것을 목표로 합니다.

그 결과,
- 사역자는 감정 소모가 큰 대화에서 보호받고
- 더 많은 사람에게 더 빠르게 응답할 수 있으며
- 디지털 선교 플랫폼은 지속 가능한 구조를 갖게 됩니다.

---

## Tech at a glance

- **LLM**: Upstage (엔진 교체 가능)
- **Framework**: LangGraph
- **UI**: Streamlit
- **Data**: WhatsApp 실제 선교 대화 + Golden Dataset
- **Evaluation**: RAGAS 기반 자동 평가

---

> 이 프로젝트는 “AI가 사역을 대체한다”가 아니라,  
> **AI가 사역자가 더 중요한 일에 집중할 수 있도록 돕는 도구**를 만드는 것을 목표로 합니다.


<details>
<summary><strong>📦 Chatbot_ver2 폴더 (프로젝트 루트)</strong></summary>

이 폴더는 **데이터(data) + 데모 UI(streamlit) + 메인 챗봇 로직(노트북/스크립트)** 을 한 곳에 모아둔 프로젝트 루트입니다.  
큰 흐름은 **데이터 → (메인 챗봇 로직) → Streamlit UI로 호출**이에요.

---

<details>
<summary><strong>🗂️ 1) data/ (지식베이스 & 평가 데이터)</strong></summary>

`data/`는 챗봇이 참고하는 **원문 지식**과, 평가까지 끝난 **골든 데이터셋**을 담는 저장소입니다.

- `data/book/`  
  실제 사역자들이 사역 현장에서 사용하는 **책 13권**을  
  **영어로 번역 → 텍스트로 변환**한 *원본 텍스트*가 들어 있습니다.

- `data/golden_dataset/`  
  `book/`, `gq/`, `whatsapp 실제 대화`에서 뽑은 QnA를 모아  
  **RAGAS로 평가까지 완료한 “검증된 QnA 데이터”**가 들어 있습니다.  
  (즉, “좋은 답변”을 데이터로 쌓아가는 핵심 자산!)

- `data/gq/`  
  GotQuestions에서 수집한 **QnA 원본 데이터**가 들어 있습니다.

</details>

---

<details>
<summary><strong>🖥️ 2) streamlit/ (데모 UI 실행 폴더)</strong></summary>

`streamlit/`은 “사람이 바로 눌러서 써볼 수 있는” **채팅 UI 데모**를 위한 폴더입니다.

- `streamlit/app.py`  
  Streamlit 채팅 화면(메신저 느낌)을 구성합니다.  
  메시지 전송은 `send_message()`에서 처리하고, 여기서 챗봇 호출도 같이 합니다. :contentReference[oaicite:0]{index=0}  
  또한 `st.session_state.messages`에 대화 히스토리를 쌓고, 자동 스크롤도 붙어 있어요. :contentReference[oaicite:1]{index=1}  
  봇 로딩이 실패하면 사이드바에 에러를 친절히 띄우는 디버깅 처리도 포함되어 있습니다. :contentReference[oaicite:2]{index=2}

- `streamlit/bot_adapter.py`  
  UI(`app.py`)와 메인 챗봇 로직 사이를 이어주는 **어댑터(브릿지)** 입니다.  
  핵심은 `get_bot_reply(message, history)` → 내부에서 `run(message, session_id)`를 호출하고,  
  최종 답변 텍스트를 `final_translated` 또는 `generation`에서 꺼내 Streamlit로 돌려줍니다. :contentReference[oaicite:3]{index=3}  
  또한 프로젝트 루트를 sys.path에 추가해서 상위 로직을 import 가능하게 해둡니다. :contentReference[oaicite:4]{index=4}

- `streamlit/requirements.txt`  
  Streamlit 데모 환경 실행에 필요한 패키지 목록입니다.

- `streamlit/bible.png`  
  사이드바 프로필 이미지(아이콘)로 사용됩니다. :contentReference[oaicite:5]{index=5}

</details>

---

<details>
<summary><strong>🧠 3) 메인 챗봇 파일 (chatbot_with_MongoDB.ipynb)</strong></summary>

이 노트북은 “우리 챗봇이 실제로 똑똑해지는 부분”이 다 들어있는 **메인 로직**입니다.  
Streamlit은 UI일 뿐이고, 진짜 핵심은 여기서 돌아갑니다. (그래서 이 파일은 자세히! 😎)

### 3-1) 한 줄 요약
**MongoDB로 로그를 남기고**,  
입력을 **번역 → 라우팅 → (RAG/Default/Block/Handoff) 처리 → 다시 번역**하는  
**LangGraph 노드 기반 파이프라인**을 구성합니다.

---

### 3-2) 핵심 구성요소(중요한 것만 쏙쏙)

#### ✅ (1) 모델 & 상태(State)
- LLM은 `ChatUpstage(model="solar-pro", temperature=0)` 형태로 설정되어 있습니다.
- 대화는 `State(TypedDict)`로 관리합니다.  
  여기엔 예를 들어:
  - `session_id` : 세션 구분(브라우저/대화 단위)
  - `input_msg`, `initial_translated`, `final_translated`
  - `route` : 라우팅 결과
  - `documents`, `generation`
  - `log_steps` : 단계별 로그 누적  
  같은 필드들이 들어갑니다.

#### ✅ (2) 데이터 로딩 & 벡터DB 준비
- `data/` 폴더를 하위 폴더까지 순회하면서 텍스트를 로드하고,
- `Chroma` 기반 벡터 스토어를 만들거나 로드하는 흐름이 있습니다.  
  (즉, `data/book`, `data/gq` 같은 자료들이 “검색 가능한 지식”으로 변환되는 구간)

#### ✅ (3) 번역 노드 (입력/출력 언어 다리)
- `translate_persian_to_english()` : 사용자 입력을 내부 처리용으로 영어화
- `translate_english_to_persian()` : 최종 답변을 사용자 언어로 다시 변환  
→ Streamlit에서 페르시아어로 자연스럽게 보이게 만드는 핵심이에요.

#### ✅ (4) 라우팅(분기) + 안전장치
- `router()` / `route_query()`에서 입력을 분류해요.
- 라우팅 결과에 따라 다음 노드로 이동합니다:
  - `node_rag_responser` : 신앙 질문(근거 기반 답변)
  - `node_default_responser` : 일반 대화/가벼운 질문
  - `node_block_responser` : 욕설/광고/공격성 메시지 차단
  - `node_handoff_responser` : “사람이 봐야 하는 케이스”는 링크/안내로 넘김  
- 특히 `route_logic_with_handoff()`처럼  
  “RAG로 가기 전에 한 번 더 체크해서 handoff로 보낼지” 같은 **운영 안전장치**도 들어있습니다.

#### ✅ (5) RAG 파이프라인(검색 → 판단 → 생성)
- `judge_retrieval()` : 검색 결과가 충분한지/쓸만한지 체크
- `generate()` : 최종 답변 생성
- `rewrite_query()` : 검색이 애매하면 질문을 다시 다듬어서 재시도
- `generate_or_rewrite_query()` : 위 흐름을 묶어서 더 똑똑하게 굴리는 역할  
→ “모르면 그냥 말 만들어내기”를 줄이려는 설계 포인트입니다.

#### ✅ (6) MongoDB 로깅(운영/디버깅의 진짜 핵심)
- `append_step_log()`로 각 노드 단계의 결과를 `log_steps`에 계속 쌓고,
- `serialize_state()` / `serialize_obj()` 같은 함수로 저장 가능한 형태로 바꿔서,
- MongoDB에 “대화별/단계별 로그”를 남기는 구조입니다.  
→ 나중에 **실제 사역 대화 분석 / 오류 추적 / 품질 개선**할 때 엄청 큰 자산이 됩니다.

---

### 3-3) 최종 실행 엔트리: run()
노트북 내부에는 `run(message, session_id)`가 있어서,  
외부(Streamlit의 `bot_adapter.py`)에서 이 함수만 호출하면  
**그래프가 한 턴 실행되고 최종 state를 반환**하는 형태입니다.

> 그래서 Streamlit 쪽은 “UI + run() 호출”만 하고,  
> 모든 똑똑한 처리는 이 노트북이 담당합니다.

</details>

</details>


<details>
<summary><strong>🕸️ GotQuestions_Crawling_code 폴더 설명</strong></summary>

이 폴더는 **GotQuestions 웹사이트에서 QnA 데이터셋을 수집하기 위한 크롤링 코드**를 모아둔 곳입니다.  
Chatbot_ver2에서 사용하는 `gq/` 데이터의 **원천(raw source)** 이 바로 여기서 만들어집니다.

“챗봇이 참고할 질문·답변을 직접 모으기 위해 만든 데이터 수집용 폴더”라고 보면 됩니다.

---

### 📂 폴더 구성

- `GotQuestion_Crawling_Kor.ipynb`  
  → **한국어 GotQuestions** 페이지 크롤링 코드

- `GotQuestions_Crawling_Far.ipynb`  
  → **페르시아어(Farsi) GotQuestions** 페이지 크롤링 코드

- `GotQuestion_Crawling_Arabic.ipynb`  
  → **아랍어 GotQuestions** 페이지 크롤링 코드

각 노트북은 **언어별 GotQuestions 사이트 구조에 맞춰** 작성되었으며,  
질문(Question)과 답변(Answer)을 한 쌍으로 수집하는 것을 목표로 합니다.

---

### 🛠️ 크롤링 방식 요약

- 기본 구조
  - 질문 목록 페이지 수집
  - 개별 질문 페이지 접근
  - 질문 제목 + 본문 답변 파싱
- 수집된 데이터는
  - 텍스트 기반 QnA 형태로 정리
  - 이후 `data/gq/` 폴더로 이동해 전처리 및 RAG용 데이터로 활용됩니다.

---

### 💡 왜 언어별로 나눴을까?

GotQuestions는 **언어마다 페이지 구조와 URL 규칙이 조금씩 다르기 때문**입니다.  
하나의 범용 크롤러보다,  
언어별 노트북로 분리하는 것이 **유지보수와 수정에 훨씬 안정적**이었습니다.

---

> 이 폴더는 “챗봇이 똑똑해지기 위한 재료를 직접 수집하는 단계”에 해당하며,  
> 이후 데이터 정제 → Golden Dataset → RAG 파이프라인으로 이어지는 출발점 역할을 합니다.

</details>



<details>
<summary><strong>🧪 evaluation/ 폴더 설명 (Golden Dataset 만들고, RAGAS로 계속 점검하기)</strong></summary>

여기는 한마디로 **“QnA를 만들고 → 점수 매기고 → 더 좋은 답변으로 고쳐가는”** 실험실입니다 🔬  
GotQuestions 원본 답변이 너무 길거나(실사용에 부적합), 모델 답변 품질을 수치로 보고 싶을 때  
이 폴더의 노트북들이 순서대로 돌아가요.

---

## ✅ 전체 흐름(3단계)

1) **GQ 답변 요약** →  
2) **요약 후보 3개 만들고, RAGAS로 “베스트 요약” 선택** →  
3) **만든 QnA 데이터셋(=모범답안) vs 우리 챗봇 답변**을 RAGAS로 비교 평가  
→ 점수 낮은 케이스를 보고 **프롬프트/지식베이스/라우팅을 개선**해서 Golden Dataset으로 다듬습니다.

---

<details>
<summary><strong>1) GQ_summary_with_ai.ipynb — GotQuestions 답변 “짧게” 만들기</strong></summary>

GotQuestions의 답변은 길~고 설명형이라, 채팅에서 그대로 쓰기엔 부담이 있어요.  
그래서 이 노트북은:

- 엑셀로 저장된 GQ QnA를 불러온 다음
- **“채팅에서 자연스럽게 말하는 2–4문장 요약 답변”**을 생성해서
- `GQ_Summarized_Full.xlsx` 같은 형태로 저장합니다.

추가로,
- 원문 답변 vs 요약 답변이 너무 동떨어졌는지 확인하려고  
  TF-IDF 기반 **유사도(Similarity) 점수**도 간단히 계산해서 체크합니다.

</details>

---

<details>
<summary><strong>2) evaluation_with_ragas.ipynb — 요약 3개 만들고, RAGAS로 “베스트” 고르기</strong></summary>

여기가 Golden Dataset 제작에서 **가장 핵심 파이프라인**이에요 ⭐

### (A) 요약 후보 3개 생성
- 같은 질문/원문 답변에 대해 **요약 답변을 3가지 버전(Summary1~3)**으로 생성합니다.
- 현실적인 이유(중간 멈춤/에러) 때문에:
  - **10개 단위로 중간 저장**
  - 멈춘 지점부터 다시 돌릴 수 있는 **resume 로직**이 들어가 있어요.

### (B) RAGAS로 3개 후보 평가
각 Summary 후보를 아래 지표로 평가합니다:
- **Relevancy**: 질문에 잘 대답했는지
- **Correctness**: 내용이 사실/정확한지
- **Similarity**: 기준 답안(또는 원문)과 의미적으로 얼마나 유사한지

그리고 세 점수에 가중치를 줘서 **Weighted Score**를 만들고,
- 점수가 제일 높은 요약을 `Best_Summary`로 선택합니다.
- 결과적으로 “요약 후보 3개 + 점수 + 최종 선택본”이 합쳐진  
  **QnA 데이터셋**이 만들어집니다.

> 요약을 ‘그냥 생성’하는 게 아니라  
> **생성 → 평가 → 선택**으로 굴려서 데이터 품질을 올리는 구조예요.

</details>

---

<details>
<summary><strong>3) finaltest_with_ragas.ipynb — 모범답안 vs 우리 챗봇 답변, 최종 대결</strong></summary>

이 노트북은 만들어진 QnA 데이터셋(=모범답안)을 기준으로  
**우리 챗봇이 실제로 얼마나 잘 답하는지**를 점수로 확인합니다.

- 입력: 질문(Question), 모범 답변(예: Chatbot_Summary), 챗봇 답변(예: AI_Answer1)
- 평가 지표:
  - **Answer Similarity**를 기본 점수로 보고
  - **Answer Correctness**를 가산/감점처럼 함께 반영해서 비교합니다.
- 배치 단위로 평가하면서 **중간 저장**도 해서, 긴 데이터도 안정적으로 돌릴 수 있어요.

이 결과를 보고,
- 점수 낮은 케이스를 골라서
- **프롬프트 수정 / 데이터 보강 / 라우팅 개선**을 반복하면  
데이터셋이 점점 “진짜 Golden”해집니다 ✨

</details>

---

<details>
<summary><strong>+ chatbot_for_evaluation.ipynb (보조)</strong></summary>

이 노트북은 평가를 위해 **“질문 리스트에 대해 우리 챗봇 답변을 뽑아오는 용도”**로 사용됩니다.  
즉, `finaltest_with_ragas.ipynb`에서 비교할 **챗봇 답변 컬럼(AI_Answer*)**을 만드는 쪽에 가깝습니다.

</details>

</details>



<details>
<summary><strong>📱 puppeteer_whatsappcrawling 폴더 설명</strong></summary>

이 폴더는 **Puppeteer를 이용해 WhatsApp Web에서 실제 사역 대화를 크롤링**하기 위한 코드입니다.  
여기서 수집된 대화는 이후 **WhatsApp QnA 데이터셋**을 만들기 위한 원천 데이터로 사용되었습니다.

즉,  
👉 *“현장에서 실제로 오간 대화를 데이터로 바꾸는 단계”*에 해당합니다.

---

## 📂 폴더 구성

- `whatsapp_crawling_puppeteer.js`  
  WhatsApp Web에 접속해 **모든 채팅방의 대화를 자동으로 추출**하는 메인 크롤러 스크립트입니다.

- `myUserDataDirWhatsApp/`  
  Puppeteer가 사용하는 **Chrome 사용자 데이터 디렉토리**  
  (로그인 세션 유지용 – QR 재로그인 최소화)

- `whatsapp_exports/`  
  크롤링 결과가 **채팅방별 `.txt` 파일**로 저장되는 폴더

- `whatsapp_user_data/`  
  테스트 및 사용자별 크롤링 데이터를 분리해 관리하기 위한 디렉토리

- `package.json`, `package-lock.json`  
  Puppeteer 실행을 위한 Node.js 환경 설정

---

## 🛠️ 크롤링 방식 요약

### 1️⃣ WhatsApp Web 자동 접속
- Puppeteer로 Chrome을 실행하고
- WhatsApp Web에 접속한 뒤
- **QR 코드는 최초 1회 수동 로그인**으로 처리합니다.
- 이후에는 `userDataDir`를 사용해 로그인 상태를 유지합니다.

### 2️⃣ 채팅 목록 전체 수집
- 왼쪽 채팅 리스트를 **자동 스크롤**해
- 계정에 존재하는 모든 채팅방을 로드합니다.
- 채팅 이름은
  - `last seen`, 시간 표시, 시스템 문구를 제외하고
  - 최대한 “사람 이름/대화 이름”만 남기도록 여러 조건을 거쳐 추출합니다.

### 3️⃣ 채팅방별 메시지 추출
각 채팅방에 대해 다음 과정을 반복합니다.

- 채팅 클릭
- 메시지 영역을 **맨 위까지 스크롤**
- 모든 메시지를 순회하며:
  - 발신자 구분 (`Me` / `Contact` / `System`)
  - 시간 정보
  - 메시지 텍스트
  를 함께 추출합니다.

시스템 메시지(입장, 퇴장 등)는 따로 표시해 구분합니다.

### 4️⃣ 텍스트(.txt)로 저장
- 채팅방 하나당 **하나의 `.txt` 파일**로 저장
- 형식은 실제 WhatsApp 대화 로그와 최대한 유사하게 구성
- 모든 채팅을 하나로 합친 `all_chats_combined.txt`도 함께 생성합니다.

---

## 💡 왜 Puppeteer를 사용했을까?

- WhatsApp은 공식 API로 **과거 대화 전체를 가져오는 것이 매우 제한적**이고
- 실제 사역 계정의 대화를 그대로 수집하려면
  👉 **브라우저 자동화 방식이 가장 현실적인 선택**이었습니다.

이 방식 덕분에:
- 가공되지 않은 **현장 그대로의 대화 데이터**를 확보할 수 있었고
- 이후 QnA 추출 → 정제 → Golden Dataset 구축까지 이어질 수 있었습니다.

---

> 이 폴더에서 만들어진 `.txt` 대화 로그는  
> 전처리를 거쳐 **WhatsApp 기반 QnA 데이터셋**으로 변환되었고,  
> 최종적으로 Chatbot_ver2의 RAG 지식 및 평가 데이터로 활용됩니다.

</details>



