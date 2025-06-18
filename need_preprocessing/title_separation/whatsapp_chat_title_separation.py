import os
import re
import json
import pandas as pd
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import openai
from pathlib import Path
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TopicScore:
    """주제별 점수를 저장하는 클래스"""
    topic: str
    score: int  # 1-5 스케일

@dataclass
class QAData:
    """질문-답변 데이터를 저장하는 클래스"""
    question: str
    answer: str
    topic_scores: List[TopicScore]
    file_source: str
    timestamp: str

class WhatsAppParser:
    """WhatsApp 채팅 파일을 파싱하는 클래스"""
    
    def __init__(self):
        # WhatsApp 메시지 패턴 (한국어/영어 시간 형식 모두 지원)
        self.message_pattern = re.compile(
            r'\[([\d\. :오전오후]+)\] ([^:]+): (.+)'
        )
    
    def parse_file(self, file_path: str) -> List[Dict]:
        """
        WhatsApp 채팅 파일을 파싱하여 메시지 리스트 반환
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            messages = []
            for line in content.split('\n'):
                if line.strip():
                    match = self.message_pattern.match(line)
                    if match:
                        timestamp, sender, message = match.groups()
                        messages.append({
                            'timestamp': timestamp,
                            'sender': sender,
                            'message': message.strip()
                        })
            
            return messages
        except Exception as e:
            logger.error(f"파일 파싱 오류 {file_path}: {e}")
            return []
    
    def extract_qa_pairs(self, messages: List[Dict]) -> List[Tuple[Dict, Dict]]:
        """
        메시지에서 질문-답변 쌍을 추출
        질문자와 답변자가 다른 경우를 찾음
        """
        qa_pairs = []
        
        for i in range(len(messages) - 1):
            current_msg = messages[i]
            next_msg = messages[i + 1]
            
            # 발신자가 다르고, 현재 메시지가 질문 형태인지 확인
            if (current_msg['sender'] != next_msg['sender'] and 
                self._is_question(current_msg['message'])):
                
                qa_pairs.append((current_msg, next_msg))
        
        return qa_pairs
    
    def _is_question(self, message: str) -> bool:
        """
        메시지가 질문인지 판단 (개선된 휴리스틱)
        """
        message_lower = message.lower()
        
        # 명확한 질문 표시
        if message.endswith('?'):
            return True
            
        # 질문 시작 패턴
        question_starters = [
            'can i', 'can you', 'could you', 'would you', 'do you', 'did you',
            'will you', 'are you', 'is it', 'how', 'what', 'why', 'when', 
            'where', 'who', 'which', 'we heard that', 'i heard that'
        ]
        
        # 답변 시작 패턴 (질문이 아님을 나타냄)
        answer_starters = [
            'counselor:', 'oh, honey', 'hello', 'i understand', 'that\'s a',
            'i hear your', 'while some', 'jesus promises', 'we do not'
        ]
        
        # 답변 패턴이 있으면 질문이 아님
        if any(message_lower.startswith(pattern) for pattern in answer_starters):
            return False
            
        # 질문 패턴이 있으면 질문임
        if any(pattern in message_lower for pattern in question_starters):
            return True
            
        return False

class TopicClassifier:
    """OpenAI API를 사용한 주제 분류기"""
    
    def __init__(self, api_key: str, topics: List[str]):
        openai.api_key = api_key
        self.topics = topics
    
    def classify_question(self, question: str) -> List[TopicScore]:
        """
        질문을 주제별로 1-5 스케일로 분류
        """
        prompt = self._create_classification_prompt(question)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a religious dialogue expert who classifies questions by topics."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            return self._parse_classification_result(result)
            
        except Exception as e:
            logger.error(f"분류 오류: {e}")
            # 기본값 반환
            return [TopicScore(topic, 1) for topic in self.topics]
    
    def _create_classification_prompt(self, question: str) -> str:
        """
        분류를 위한 프롬프트 생성
        """
        topics_str = ", ".join(self.topics)
        
        return f"""
다음 질문을 주제별로 1-5 스케일로 평가해주세요:

질문: "{question}"

주제들: {topics_str}

각 주제가 이 질문과 얼마나 관련이 있는지 1(전혀 관련없음)부터 5(매우 관련있음)까지 점수를 매겨주세요.

결과를 다음 JSON 형식으로 반환해주세요:
{{
    "scores": [
        {{"topic": "주제1", "score": 점수}},
        {{"topic": "주제2", "score": 점수}},
        ...
    ]
}}
"""
    
    def _parse_classification_result(self, result: str) -> List[TopicScore]:
        """
        AI 응답을 파싱하여 TopicScore 리스트로 변환
        """
        try:
            # JSON 추출
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            json_str = result[json_start:json_end]
            
            data = json.loads(json_str)
            scores = []
            
            for item in data['scores']:
                scores.append(TopicScore(
                    topic=item['topic'],
                    score=int(item['score'])
                ))
            
            return scores
            
        except Exception as e:
            logger.error(f"결과 파싱 오류: {e}")
            return [TopicScore(topic, 1) for topic in self.topics]

class WhatsAppAnalyzer:
    """메인 분석기 클래스"""
    
    def __init__(self, openai_api_key: str, topics: List[str], min_relevance_score: int = 3):
        self.parser = WhatsAppParser()
        self.classifier = TopicClassifier(openai_api_key, topics)
        self.topics = topics
        self.min_relevance_score = min_relevance_score
        self.results = []
    
    def analyze_directory(self, directory_path: str) -> List[QAData]:
        """
        디렉토리 내 모든 txt 파일을 분석
        """
        txt_files = list(Path(directory_path).glob("*.txt"))
        logger.info(f"총 {len(txt_files)}개 파일 발견")
        
        for file_path in txt_files:
            logger.info(f"분석 중: {file_path.name}")
            self.analyze_file(str(file_path))
        
        return self.results
    
    def analyze_file(self, file_path: str):
        """
        단일 파일 분석
        """
        messages = self.parser.parse_file(file_path)
        if not messages:
            return
        
        qa_pairs = self.parser.extract_qa_pairs(messages)
        logger.info(f"{file_path}에서 {len(qa_pairs)}개 Q&A 쌍 발견")
        
        for question_msg, answer_msg in qa_pairs:
            # 주제 분류 (질문으로 분류)
            topic_scores = self.classifier.classify_question(question_msg['message'])
            
            # 관련성이 높은 주제가 있는지 확인
            if any(score.score >= self.min_relevance_score for score in topic_scores):
                qa_data = QAData(
                    question=question_msg['message'],  # 질문
                    answer=answer_msg['message'],      # 답변
                    topic_scores=topic_scores,
                    file_source=os.path.basename(file_path),
                    timestamp=question_msg['timestamp']
                )
                self.results.append(qa_data)
    
    def export_to_excel(self, output_path: str):
        """
        결과를 엑셀 파일로 저장
        """
        if not self.results:
            logger.warning("저장할 데이터가 없습니다.")
            return
        
        # 데이터 변환
        export_data = []
        for qa in self.results:
            # 주제별 점수를 문자열로 변환
            topic_str = ", ".join([f"{score.topic}({score.score})" for score in qa.topic_scores])
            
            export_data.append({
                'Question': qa.question,     # 올바른 질문
                'Answer': qa.answer,         # 올바른 답변
                'Topic': topic_str,
                'File_Source': qa.file_source,
                'Timestamp': qa.timestamp
            })
        
        # 엑셀 저장
        df = pd.DataFrame(export_data)
        df.to_excel(output_path, index=False, engine='openpyxl')
        logger.info(f"결과 저장 완료: {output_path}")
        
        # 저장된 데이터 확인을 위한 로그
        logger.info("저장된 데이터 샘플:")
        for i, row in enumerate(export_data[:2]):  # 처음 2개만 로그
            logger.info(f"행 {i+1} - Question: {row['Question'][:50]}...")
            logger.info(f"행 {i+1} - Answer: {row['Answer'][:50]}...")

# 사용 예시
def main():
    # 설정
    OPENAI_API_KEY = "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"
    TOPICS = ["복음", "사랑", "변증학", "구원", "기도", "성경"]
    INPUT_DIRECTORY = "./test_chat"
    OUTPUT_FILE = f"religious_qa_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    # 분석기 초기화
    analyzer = WhatsAppAnalyzer(
        openai_api_key=OPENAI_API_KEY,
        topics=TOPICS,
        min_relevance_score=3  # 3점 이상인 주제만 포함
    )
    
    # 분석 실행
    results = analyzer.analyze_directory(INPUT_DIRECTORY)
    
    # 결과 출력
    logger.info(f"총 {len(results)}개 종교적 Q&A 추출 완료")
    
    # 엑셀 저장
    analyzer.export_to_excel(OUTPUT_FILE)

if __name__ == "__main__":
    main()