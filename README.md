# 🙌 Digital Mission AI Chatbot  
AI 기반 디지털 선교 챗봇 (Last Call 협업 프로젝트)

본 프로젝트는 **디지털 선교 현장의 구조적 인력 부족과 응답 지연 문제**를 해결하기 위해 개발된  
**AI 기반 전도·상담 챗봇 시스템**입니다.  

Last Call 플랫폼은 연간 **약 30,000명의 신규 유입자**를 맞이하지만, 이를 감당하는 사역자는 10~20명뿐입니다.  
이 챗봇은 사역자의 업무를 경감하고, 사용자가 즉시 도움을 받을 수 있도록 설계되었습니다.

---

## 🌟 프로젝트 주요 기능

- **Adaptive Routing System**  
  block / default / rag / handoff 로 세분화된 라우팅  
- **RAG 기반 신학 지식 응답**  
  BM25 + Embedding + LLM re-ranking을 사용한 고품질 답변  
- **Handoff 기능 (사람 연결)**  
  심층 신앙 대화 필요 시 자동으로 선교사 연결  
- **Hallucination-safe Pipeline**  
  문서 기반 factfulness + relevance 검사  
- **다국어 지원 (Persian ↔ English)**  
  입력 정규화 및 응답 번역  
- **선교 현장 맞춤형 AD_CONTEXT 프롬프트**

---

## 📁 프로젝트 구조 (Overview)

Chatbot_ver2/
├── data/ # RAG 학습 데이터
├── streamlit/ # 웹 시연(Streamlit UI)
├── chatbot_revised.ipynb # 챗봇 백엔드 핵심 로직
├── requirements.txt
└── README.md

yaml
코드 복사

> 아래에서는 프로젝트가 커지는 것을 방지하기 위해  
> **각 폴더별 역할을 토글 형식으로 설명합니다.**

---

## 📂 폴더별 설명

<details>
<summary>🖥️ streamlit/ — Web Demo (UI)</summary>

`streamlit/` 폴더는 본 프로젝트의 AI 챗봇을  
**웹 환경에서 시연(demo)** 하기 위한 Streamlit 기반 프런트엔드입니다.

이 폴더의 목적은 **모델 개발이나 성능 실험이 아니라**,  
외부 사용자·협업자·심사위원에게  
👉 **“챗봇이 실제로 어떻게 동작하는지”를 직관적으로 보여주는 것**입니다.

### 위치
Chatbot_ver2/streamlit/

shell
코드 복사

### 구성 파일 및 역할

streamlit/
├── app.py
├── bot_adapter.py
├── bible.png
├── requirements.txt

yaml
코드 복사

- **app.py**  
  Streamlit 기반 웹 UI의 메인 실행 파일입니다.  
  사용자의 입력을 받아 챗봇에 전달하고, 응답을 채팅 형태로 화면에 출력합니다.

- **bot_adapter.py**  
  Streamlit UI와 챗봇 백엔드(Graph 기반 RAG 시스템)를 연결하는 어댑터 모듈입니다.  
  UI 코드가 챗봇 내부 로직에 직접 의존하지 않도록 중간 인터페이스 역할을 합니다.

- **bible.png**  
  챗봇 프로필 이미지 및 UI 시각 요소로 사용됩니다.

- **requirements.txt**  
  Streamlit 실행에 필요한 UI 관련 라이브러리 의존성을 정의합니다.

> ⚠️ 이 폴더는 **시연(demo) 목적의 UI 코드**이며,  
> 실제 챗봇 로직, RAG 파이프라인, 라우팅 및 평가 로직은  
> 상위 디렉토리의 `chatbot_revised.ipynb`에 정의되어 있습니다.

</details>

---

## 🚀 실행 방법 (요약)

git clone https://github.com/yourname/Chatbot_ver2.git
cd Chatbot_ver2
pip install -r requirements.txt

cd streamlit
streamlit run app.py

yaml
코드 복사

---

## 🎯 프로젝트 목표 요약

- 사역자 1명이 감당할 수 있는 사용자 수 **5배 이상 증가**  
- 평균 응답 지연 **347.8분 → 즉시(30초 이내)**  
- 악성 사용자 자동 필터링으로 감정 노동 감소  
- 심층 신앙 대화는 사람에게 전달하는 **Hybrid Human–AI 사역 모델**
