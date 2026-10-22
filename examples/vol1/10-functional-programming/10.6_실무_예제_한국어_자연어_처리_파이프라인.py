"""1권 Chapter 10: 함수형 프로그래밍 — 10.6 실무 예제: 한국어 자연어 처리 파이프라인

원고: manuscript/chapters/10-functional-programming.md (1224줄부터)
"""

# ---- 원고 1224줄 ----
import re
from functools import reduce, partial
from collections import Counter, defaultdict
from typing import List, Dict, Callable, Any

class KoreanNLPPipeline:
    """한국어 자연어 처리 파이프라인"""
    
    def __init__(self):
        self.processors = []
        self.statistics = defaultdict(int)
        self.korean_stopwords = {
            "이", "그", "저", "것", "들", "수", "등", "및", "또는", 
            "하지만", "그러나", "따라서", "즉", "때문에", "통해",
            "에서", "에게", "에는", "으로", "로", "와", "과", "을", "를"
        }
    
    def add_processor(self, name: str, processor_func: Callable[[str], str]):
        """처리기 추가"""
        self.processors.append((name, processor_func))
        return self
    
    def create_korean_normalizer(self):
        """한국어 정규화 처리기 생성"""
        def normalize(text: str) -> str:
            # 같은 자음/모음이 세 번 이상 이어지면 하나로 (ㅋㅋㅋ → ㅋ, ㅠㅠ는 그대로)
            text = re.sub(r'([ㄱ-ㅎㅏ-ㅣ])\1{2,}', r'\1', text)
            
            # 연속된 특수문자 정리
            text = re.sub(r'([!?~.])\1{2,}', r'\1', text)
            
            # 연속된 공백 정리
            text = re.sub(r'\s+', ' ', text)
            
            return text.strip()
        
        return normalize
    
    def create_korean_tokenizer(self, include_particles: bool = False):
        """한국어 토크나이저 생성"""
        def tokenize(text: str) -> str:
            # 간단한 공백 기반 토크나이징
            tokens = text.split()
            
            if not include_particles:
                # 조사/어미 제거 (매우 단순한 방식)
                cleaned_tokens = []
                for token in tokens:
                    # 일반적인 조사들 제거
                    for particle in ['은', '는', '이', '가', '을', '를', '의', '에', '로', '와', '과']:
                        if token.endswith(particle) and len(token) > len(particle):
                            token = token[:-len(particle)]
                            break
                    cleaned_tokens.append(token)
                tokens = cleaned_tokens
            
            return ' '.join(tokens)
        
        return tokenize
    
    def create_stopword_remover(self, custom_stopwords: set = None):
        """불용어 제거기 생성"""
        stopwords = self.korean_stopwords.copy()
        if custom_stopwords:
            stopwords.update(custom_stopwords)
        
        def remove_stopwords(text: str) -> str:
            tokens = text.split()
            filtered_tokens = [
                token for token in tokens 
                if token not in stopwords and len(token) > 1
            ]
            return ' '.join(filtered_tokens)
        
        return remove_stopwords
    
    def create_length_filter(self, min_length: int = 2, max_length: int = 50):
        """길이 기반 필터 생성"""
        def filter_by_length(text: str) -> str:
            tokens = text.split()
            filtered_tokens = [
                token for token in tokens 
                if min_length <= len(token) <= max_length
            ]
            return ' '.join(filtered_tokens)
        
        return filter_by_length
    
    def process_single(self, text: str) -> Dict[str, Any]:
        """단일 텍스트 처리"""
        if not isinstance(text, str):
            return {"error": "입력이 문자열이 아닙니다", "original": text}
        
        result = {
            "original": text,
            "processed": text,
            "steps": []
        }
        
        current_text = text
        
        for step_name, processor in self.processors:
            try:
                processed_text = processor(current_text)
                result["steps"].append({
                    "step": step_name,
                    "before": current_text,
                    "after": processed_text
                })
                current_text = processed_text
                self.statistics[f"{step_name}_success"] += 1
                
            except Exception as e:
                result["steps"].append({
                    "step": step_name,
                    "error": str(e)
                })
                self.statistics[f"{step_name}_error"] += 1
                break
        
        result["processed"] = current_text
        result["token_count"] = len(current_text.split()) if current_text else 0
        
        return result
    
    def process_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """배치 처리"""
        return [self.process_single(text) for text in texts]
    
    def analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """결과 분석"""
        total_texts = len(results)
        successful_results = [r for r in results if "error" not in r]
        
        # 토큰 통계
        all_tokens = []
        for result in successful_results:
            tokens = result["processed"].split()
            all_tokens.extend(tokens)
        
        token_frequency = Counter(all_tokens)
        
        # 길이 통계
        original_lengths = [len(r["original"]) for r in results if "original" in r]
        processed_lengths = [len(r["processed"]) for r in successful_results]
        
        return {
            "총_텍스트_수": total_texts,
            "성공_처리_수": len(successful_results),
            "실패_처리_수": total_texts - len(successful_results),
            "평균_원문_길이": sum(original_lengths) / len(original_lengths) if original_lengths else 0,
            "평균_처리후_길이": sum(processed_lengths) / len(processed_lengths) if processed_lengths else 0,
            "총_토큰_수": len(all_tokens),
            "고유_토큰_수": len(set(all_tokens)),
            "빈출_토큰_TOP10": token_frequency.most_common(10),
            "처리_단계_통계": dict(self.statistics)
        }

# 감성 분석 파이프라인
def create_korean_sentiment_analyzer():
    """한국어 감성 분석기 생성"""
    
    # 간단한 감성 사전 (실제로는 더 복잡한 사전이 필요)
    positive_words = {
        "좋은", "훌륭한", "멋진", "최고", "완벽한", "만족", "기쁜", "행복한", 
        "사랑", "즐거운", "신나는", "놀라운", "감동", "고마운", "편안한", "재미있는"
    }
    
    negative_words = {
        "나쁜", "끔찍한", "최악", "불만", "화난", "슬픈", "아쉬운", "실망", 
        "짜증", "힘든", "어려운", "문제", "고민", "걱정", "스트레스", "지친"
    }
    
    def analyze_sentiment(text: str) -> Dict[str, Any]:
        tokens = text.split()
        
        positive_count = sum(1 for token in tokens if token in positive_words)
        negative_count = sum(1 for token in tokens if token in negative_words)
        
        # 감성 점수 계산 (-1 ~ 1)
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            sentiment_score = 0
            sentiment_label = "중립"
        else:
            sentiment_score = (positive_count - negative_count) / total_sentiment_words
            if sentiment_score > 0.2:
                sentiment_label = "긍정"
            elif sentiment_score < -0.2:
                sentiment_label = "부정"
            else:
                sentiment_label = "중립"
        
        return {
            "감성_점수": round(sentiment_score, 3),
            "감성_라벨": sentiment_label,
            "긍정_단어_수": positive_count,
            "부정_단어_수": negative_count,
            "감성_단어_비율": round(total_sentiment_words / len(tokens) * 100, 1) if tokens else 0,
            "발견된_긍정_단어": [token for token in tokens if token in positive_words],
            "발견된_부정_단어": [token for token in tokens if token in negative_words]
        }
    
    return analyze_sentiment

# 파이프라인 사용 예제
def demonstrate_nlp_pipeline():
    """NLP 파이프라인 시연"""
    
    # 샘플 텍스트
    sample_texts = [
        "안녕하세요!!! 파이썬을 배우는 것이 정말 재미있어요~~~ ㅋㅋㅋ",
        "데이터 분석은 어렵지만 매우 흥미로운 분야입니다. 열심히 공부하고 있어요!",
        "오늘 프로그래밍 과제가 너무 힘들었어요... 스트레스 받네요 ㅠㅠ",
        "새로운 라이브러리를 배우니까 정말 놀랍고 신나는 경험이에요!",
        "버그 때문에 몇 시간을 고생했지만, 결국 해결해서 기뻐요!"
    ]
    
    # 파이프라인 구성
    pipeline = KoreanNLPPipeline()
    
    # 처리기들 추가
    pipeline.add_processor("정규화", pipeline.create_korean_normalizer())
    pipeline.add_processor("토크나이징", pipeline.create_korean_tokenizer(include_particles=False))
    pipeline.add_processor("불용어제거", pipeline.create_stopword_remover())
    pipeline.add_processor("길이필터", pipeline.create_length_filter(min_length=2, max_length=15))
    
    print("한국어 NLP 파이프라인 처리 중...")
    
    # 배치 처리
    results = pipeline.process_batch(sample_texts)
    
    # 결과 출력
    print(f"\n처리 결과:")
    for i, result in enumerate(results, 1):
        print(f"\n텍스트 {i}:")
        print(f"  원문: {result['original']}")
        print(f"  처리후: {result['processed']}")
        print(f"  토큰 수: {result['token_count']}")
    
    # 전체 분석
    analysis = pipeline.analyze_results(results)
    print(f"\n전체 분석 결과:")
    for key, value in analysis.items():
        if key == "빈출_토큰_TOP10":
            print(f"  {key}:")
            for token, count in value:
                print(f"    '{token}': {count}회")
        else:
            print(f"  {key}: {value}")
    
    # 감성 분석 추가
    sentiment_analyzer = create_korean_sentiment_analyzer()
    
    print(f"\n감성 분석 결과:")
    for i, result in enumerate(results, 1):
        sentiment = sentiment_analyzer(result['processed'])
        print(f"\n텍스트 {i}: {sentiment['감성_라벨']} ({sentiment['감성_점수']})")
        if sentiment['발견된_긍정_단어']:
            print(f"  긍정 단어: {sentiment['발견된_긍정_단어']}")
        if sentiment['발견된_부정_단어']:
            print(f"  부정 단어: {sentiment['발견된_부정_단어']}")

# 실행
demonstrate_nlp_pipeline()
