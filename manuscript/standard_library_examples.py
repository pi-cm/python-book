"""
표준 라이브러리 실용 예제 모음
한국어 컨텍스트를 활용한 실무 예제들
"""

import re
import json
import csv
import datetime
from zoneinfo import ZoneInfo
from collections import Counter, defaultdict
import urllib.parse
import urllib.request
import statistics
import threading
import os
import logging


class KoreanTextProcessor:
    """한국어 텍스트 처리 클래스"""
    
    def __init__(self):
        # 한글 패턴들 (단어 경계를 고려한 정확한 패턴)
        self.korean_name_pattern = re.compile(r'[가-힣]{2,4}(?=\s|$)')  # 한글 이름
        self.phone_pattern = re.compile(r'010-\d{4}-\d{4}')
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    
    def extract_korean_names(self, text):
        """텍스트에서 한국어 이름 추출"""
        return self.korean_name_pattern.findall(text)
    
    def extract_phone_numbers(self, text):
        """텍스트에서 전화번호 추출"""
        return self.phone_pattern.findall(text)
    
    def extract_emails(self, text):
        """텍스트에서 이메일 추출"""
        return self.email_pattern.findall(text)


class KoreanTimeHandler:
    """한국 시간 처리 클래스"""
    
    def __init__(self):
        self.seoul_tz = ZoneInfo("Asia/Seoul")
        self.korean_holidays = {
            (1, 1): "신정",
            (3, 1): "삼일절",
            (5, 5): "어린이날",
            (6, 6): "현충일",
            (8, 15): "광복절",
            (10, 3): "개천절",
            (10, 9): "한글날",
            (12, 25): "크리스마스"
        }
    
    def get_korean_time(self):
        """현재 한국 시간 반환"""
        return datetime.datetime.now(self.seoul_tz)
    
    def is_holiday(self, date):
        """주어진 날짜가 한국 공휴일인지 확인"""
        return (date.month, date.day) in self.korean_holidays
    
    def format_korean_date(self, dt):
        """한국식 날짜 포맷"""
        return dt.strftime('%Y년 %m월 %d일')


class KoreanDataHandler:
    """한국어 데이터 직렬화 처리 클래스"""
    
    @staticmethod
    def save_json(data, filename):
        """한글이 깨지지 않게 JSON 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def load_json(filename):
        """JSON 파일 로드"""
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def save_csv(data, filename, fieldnames):
        """한글 CSV 저장"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    
    @staticmethod
    def load_csv(filename):
        """CSV 파일 로드"""
        with open(filename, 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f))


class KoreanURLEncoder:
    """한국어 URL 처리 클래스"""
    
    @staticmethod
    def encode_korean_url(korean_text):
        """한글을 URL 인코딩"""
        return urllib.parse.quote(korean_text, safe='')
    
    @staticmethod
    def decode_korean_url(encoded_text):
        """URL 인코딩된 한글 디코딩"""
        return urllib.parse.unquote(encoded_text)
    
    @staticmethod
    def build_search_url(base_url, query, **params):
        """검색 URL 생성"""
        params['q'] = query
        encoded_params = urllib.parse.urlencode(params)
        return f"{base_url}?{encoded_params}"


class KoreanFinanceCalculator:
    """한국 금융 계산 클래스"""
    
    @staticmethod
    def compound_interest(principal, annual_rate, years, compounds_per_year=12):
        """복리 이자 계산"""
        return principal * (1 + annual_rate / compounds_per_year) ** (compounds_per_year * years)
    
    @staticmethod
    def monthly_savings_plan(monthly_amount, annual_rate, years):
        """월 적금 계산"""
        total_months = years * 12
        monthly_rate = annual_rate / 12
        
        # 각 월별 적금이 만기까지 벌어들이는 이자 계산
        total_amount = 0
        for month in range(total_months):
            remaining_months = total_months - month
            amount_with_interest = monthly_amount * (1 + monthly_rate) ** remaining_months
            total_amount += amount_with_interest
        
        return total_amount
    
    @staticmethod
    def stock_transaction_cost(price, shares, commission_rate=0.00015):
        """주식 거래 비용 계산"""
        total_cost = price * shares
        commission = total_cost * commission_rate
        return {
            'total_cost': total_cost,
            'commission': commission,
            'final_cost': total_cost + commission
        }


class KoreanStatisticsAnalyzer:
    """한국 데이터 통계 분석 클래스"""
    
    def __init__(self):
        self.city_populations = {
            "서울": 972.1,
            "부산": 341.4,
            "인천": 246.6,
            "대구": 153.8,
            "대전": 150.2,
            "광주": 103.5,
            "울산": 103.4,
        }
    
    def get_population_stats(self):
        """도시 인구 통계"""
        populations = list(self.city_populations.values())
        return {
            'mean': statistics.mean(populations),
            'median': statistics.median(populations),
            'stdev': statistics.stdev(populations),
            'min': min(populations),
            'max': max(populations)
        }
    
    def analyze_data_distribution(self, data):
        """데이터 분포 분석"""
        if not data:
            return {}
        
        return {
            'count': len(data),
            'mean': statistics.mean(data),
            'median': statistics.median(data),
            'mode': statistics.mode(data) if len(set(data)) < len(data) else None,
            'stdev': statistics.stdev(data) if len(data) > 1 else 0,
            'variance': statistics.variance(data) if len(data) > 1 else 0
        }


class KoreanCollectionProcessor:
    """한국어 컬렉션 처리 클래스"""
    
    @staticmethod
    def analyze_text_frequency(text):
        """텍스트 단어 빈도 분석"""
        # 문장 부호 제거 및 단어 분리
        cleaned_text = re.sub(r'[.,!?]', '', text)
        words = cleaned_text.split()
        return Counter(words)
    
    @staticmethod
    def group_students_by_city(students):
        """학생들을 도시별로 그룹화"""
        grouped = defaultdict(list)
        for name, city in students:
            grouped[city].append(name)
        return dict(grouped)
    
    @staticmethod
    def get_top_n(counter, n=5):
        """상위 N개 항목 반환"""
        return counter.most_common(n)


class KoreanLogger:
    """한국어 로깅 시스템"""
    
    def __init__(self, name='한국_서비스'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # 한글 지원 포맷터
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s - %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def log_user_action(self, username, action):
        """사용자 행동 로깅"""
        self.logger.info(f"사용자 '{username}'님이 '{action}' 작업을 수행했습니다")
    
    def log_error(self, operation, error):
        """에러 로깅"""
        self.logger.error(f"{operation} 중 오류 발생: {str(error)}")


class KoreanConcurrencyManager:
    """한국어 동시성 처리 매니저"""
    
    def __init__(self):
        self.data_lock = threading.Lock()
        self.shared_data = {"counter": 0, "messages": []}
    
    def safe_increment(self, worker_id, increment=1):
        """스레드 안전한 카운터 증가"""
        with self.data_lock:
            self.shared_data["counter"] += increment
            self.shared_data["messages"].append(f"작업자_{worker_id}: 카운터 증가")
    
    def get_current_state(self):
        """현재 상태 반환"""
        with self.data_lock:
            return self.shared_data.copy()
    
    def reset(self):
        """상태 초기화"""
        with self.data_lock:
            self.shared_data = {"counter": 0, "messages": []}


class KoreanSystemManager:
    """한국어 시스템 관리 클래스"""
    
    @staticmethod
    def set_korean_environment():
        """한국어 환경변수 설정"""
        os.environ['LANG'] = 'ko_KR.UTF-8'
        os.environ['한국_서비스_설정'] = 'production'
    
    @staticmethod
    def get_korean_env(key, default='설정되지 않음'):
        """한국어 환경변수 조회"""
        return os.environ.get(key, default)
    
    @staticmethod
    def run_korean_subprocess(command):
        """한국어 출력을 지원하는 서브프로세스 실행"""
        import subprocess
        import sys
        
        try:
            result = subprocess.run(
                [sys.executable, "-c", command],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e)
            }


# 모든 기능을 통합한 팩토리 클래스
class KoreanStandardLibraryFactory:
    """한국어 표준 라이브러리 기능 팩토리"""
    
    @staticmethod
    def create_text_processor():
        return KoreanTextProcessor()
    
    @staticmethod
    def create_time_handler():
        return KoreanTimeHandler()
    
    @staticmethod
    def create_data_handler():
        return KoreanDataHandler()
    
    @staticmethod
    def create_url_encoder():
        return KoreanURLEncoder()
    
    @staticmethod
    def create_finance_calculator():
        return KoreanFinanceCalculator()
    
    @staticmethod
    def create_statistics_analyzer():
        return KoreanStatisticsAnalyzer()
    
    @staticmethod
    def create_collection_processor():
        return KoreanCollectionProcessor()
    
    @staticmethod
    def create_logger(name='한국_서비스'):
        return KoreanLogger(name)
    
    @staticmethod
    def create_concurrency_manager():
        return KoreanConcurrencyManager()
    
    @staticmethod
    def create_system_manager():
        return KoreanSystemManager()


if __name__ == "__main__":
    # 사용 예제
    factory = KoreanStandardLibraryFactory()
    
    # 텍스트 처리 테스트
    text_processor = factory.create_text_processor()
    sample_text = "김철수의 전화번호는 010-1234-5678이고, 이메일은 kim@example.com입니다."
    
    names = text_processor.extract_korean_names(sample_text)
    phones = text_processor.extract_phone_numbers(sample_text)
    emails = text_processor.extract_emails(sample_text)
    
    print(f"이름: {names}")
    print(f"전화번호: {phones}")
    print(f"이메일: {emails}")
    
    # 시간 처리 테스트
    time_handler = factory.create_time_handler()
    korean_time = time_handler.get_korean_time()
    formatted = time_handler.format_korean_date(korean_time)
    print(f"현재 한국 시간: {formatted}")
    
    # 통계 분석 테스트
    stats_analyzer = factory.create_statistics_analyzer()
    pop_stats = stats_analyzer.get_population_stats()
    print(f"도시 인구 평균: {pop_stats['mean']:.1f}만 명")