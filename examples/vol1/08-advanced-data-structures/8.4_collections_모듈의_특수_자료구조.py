"""1권 Chapter 8: 고급 데이터 구조 — 8.4 collections 모듈의 특수 자료구조

원고: manuscript/chapters/08-advanced-data-structures.md (604줄부터)
"""

# ---- 원고 604줄 ----
from collections import deque, defaultdict, Counter, ChainMap
from typing import Any, Optional
import time

class TaskQueue:
    """작업 큐 (deque 활용)"""
    
    def __init__(self, maxsize: Optional[int] = None):
        self.queue = deque(maxlen=maxsize)
        self.completed = deque(maxlen=100)  # 완료된 작업 최대 100개 보관
    
    def add_task(self, task: str, priority: bool = False):
        """작업 추가 (우선순위 작업은 앞에 추가)"""
        if priority:
            self.queue.appendleft(f"{task}")
            print(f"긴급 작업 추가: {task}")
        else:
            self.queue.append(task)
            print(f"일반 작업 추가: {task}")
    
    def process_task(self) -> Optional[str]:
        """다음 작업 처리"""
        if not self.queue:
            return None
        
        task = self.queue.popleft()
        self.completed.append(f"{task} (완료시간: {time.strftime('%H:%M:%S')})")
        print(f"작업 처리: {task}")
        return task
    
    def get_status(self) -> dict:
        """큐 상태 반환"""
        return {
            "대기중": list(self.queue),
            "완료됨": list(self.completed),
            "대기_작업_수": len(self.queue)
        }

# 작업 큐 시연
def demonstrate_task_queue():
    """작업 큐 시연"""
    queue = TaskQueue(maxsize=5)
    
    # 일반 작업들 추가
    queue.add_task("데이터베이스 백업")
    queue.add_task("보고서 작성")
    queue.add_task("코드 리뷰")
    
    # 긴급 작업 추가
    queue.add_task("서버 장애 처리", priority=True)
    queue.add_task("고객 문의 응답", priority=True)
    
    print(f"\n큐 상태: {queue.get_status()['대기_작업_수']}개 대기중")
    
    # 작업 처리
    for _ in range(3):
        queue.process_task()
    
    status = queue.get_status()
    print(f"\n남은 대기 작업: {status['대기중']}")
    print(f"완료된 작업: {status['완료됨']}")

demonstrate_task_queue()

# ---- 원고 684줄 ----
from collections import defaultdict, Counter

a = [1, 1, 1, 2, 2, 3, 3, 3, 3, 3]
counts = Counter(a)
print(counts)                 # Counter({3: 5, 1: 3, 2: 2})
print(counts.most_common(1))  # [(3, 5)]
print(counts[7])              # 0 (없는 값은 0개)

groups = defaultdict(list)    # 없는 키는 빈 리스트로 시작
for word in ["사과", "바나나", "수박", "배"]:
    groups[len(word)].append(word)
print(dict(groups))           # {2: ['사과', '수박'], 3: ['바나나'], 1: ['배']}

# ---- 원고 703줄 ----
from collections import defaultdict, Counter, namedtuple
from typing import Dict, List
import re

class KoreanTextStats:
    """한국어 텍스트 통계 분석기"""
    
    def __init__(self):
        self.word_frequency = Counter()
        self.sentence_lengths = defaultdict(int)
        self.pos_patterns = defaultdict(list)  # 품사별 패턴
        
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """텍스트 종합 분석"""
        # 문장 분리
        sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
        
        # 단어 분리 및 빈도 계산
        words = []
        for sentence in sentences:
            sentence_words = sentence.split()
            words.extend(sentence_words)
            
            # 문장 길이별 분포
            length_category = self._categorize_sentence_length(len(sentence))
            self.sentence_lengths[length_category] += 1
        
        # 단어 빈도 업데이트
        self.word_frequency.update(words)
        
        # 품사 패턴 분석 (간단한 규칙 기반)
        self._analyze_pos_patterns(words)
        
        return {
            "총_문장_수": len(sentences),
            "총_단어_수": len(words),
            "고유_단어_수": len(set(words)),
            "평균_문장_길이": sum(len(s) for s in sentences) / len(sentences) if sentences else 0,
            "문장_길이_분포": dict(self.sentence_lengths),
            "빈출_단어": self.word_frequency.most_common(10),
            "품사_패턴": {k: len(v) for k, v in self.pos_patterns.items()}
        }
    
    def _categorize_sentence_length(self, length: int) -> str:
        """문장 길이 범주화"""
        if length < 30:
            return "짧은문장"
        elif length < 60:
            return "보통문장"
        else:
            return "긴문장"
    
    def _analyze_pos_patterns(self, words: List[str]):
        """간단한 품사 패턴 분석"""
        # 한국어 조사/어미 패턴 (매우 간단한 규칙)
        for word in words:
            if word.endswith(('은', '는', '이', '가', '을', '를')):
                self.pos_patterns['조사'].append(word)
            elif word.endswith(('다', '요', '니다', '습니다')):
                self.pos_patterns['어미'].append(word)
            elif any(word.startswith(prefix) for prefix in ['안', '못', '불', '비']):
                self.pos_patterns['부정어'].append(word)
            else:
                self.pos_patterns['기타'].append(word)

# ChainMap 활용한 설정 관리
def demonstrate_chainmap():
    """ChainMap을 활용한 설정 관리"""
    # 기본 설정
    default_config = {
        "host": "localhost",
        "port": 8000,
        "debug": False,
        "database": "sqlite:///default.db"
    }
    
    # 개발 환경 설정
    dev_config = {
        "debug": True,
        "database": "sqlite:///dev.db",
        "log_level": "DEBUG"
    }
    
    # 운영 환경 설정
    prod_config = {
        "host": "production.server.com",
        "port": 80,
        "database": "postgresql://prod_db",
        "log_level": "WARNING"
    }
    
    # ChainMap으로 설정 계층 구성
    # 우선순위: 운영 > 개발 > 기본
    config = ChainMap(prod_config, dev_config, default_config)
    
    print("설정 관리 (ChainMap):")
    print(f"현재 호스트: {config['host']}")
    print(f"현재 포트: {config['port']}")  
    print(f"현재 데이터베이스: {config['database']}")
    print(f"로그 레벨: {config['log_level']}")
    print(f"디버그 모드: {config['debug']}")
    
    # 런타임에 설정 변경
    runtime_config = {"cache_timeout": 3600}
    config = config.new_child(runtime_config)  # 기존 계층 위에 한 층을 더 얹음
    
    print(f"캐시 타임아웃: {config['cache_timeout']}")
    
    # 설정 계층 확인
    print(f"\n설정 계층 수: {len(config.maps)}")
    for i, layer in enumerate(config.maps):
        print(f"  레이어 {i}: {list(layer.keys())}")

# 텍스트 분석 시연
def demonstrate_text_analysis():
    """텍스트 분석 시연"""
    sample_texts = [
        "파이썬은 프로그래밍 언어입니다. 배우기 쉽고 강력한 기능을 제공합니다.",
        "데이터 분석과 웹 개발에 널리 사용됩니다. 많은 개발자들이 선호하는 언어입니다.",
        "라이브러리가 풍부하고 커뮤니티가 활발합니다. 지속적으로 발전하고 있습니다."
    ]
    
    print("\n한국어 텍스트 분석:")
    for i, text in enumerate(sample_texts, 1):
        print(f"\n--- 텍스트 {i} 분석 ---")
        analyzer = KoreanTextStats()  # 텍스트마다 새 분석기 (통계가 섞이지 않도록)
        result = analyzer.analyze_text(text)
        
        for key, value in result.items():
            if isinstance(value, list):
                print(f"{key}: {value[:3]}...")  # 처음 3개만 표시
            else:
                print(f"{key}: {value}")

demonstrate_chainmap()
demonstrate_text_analysis()
