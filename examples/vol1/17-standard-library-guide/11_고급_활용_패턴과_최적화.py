"""1권 Chapter 17: 표준 라이브러리 핵심 가이드 — 고급 활용 패턴과 최적화

원고: manuscript/chapters/17-standard-library-guide.md (1168줄부터)
"""

# ---- 원고 1168줄 ----
from pathlib import Path
import mmap
import csv
from itertools import islice

def process_large_korean_csv(file_path, chunk_size=1000):
    """대용량 한글 CSV 파일을 청크 단위로 처리"""
    def csv_chunks(reader, size):
        while True:
            chunk = list(islice(reader, size))
            if not chunk:
                break
            yield chunk
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for chunk in csv_chunks(reader, chunk_size):
            # 각 청크별로 처리
            korean_names = [row['이름'] for row in chunk if row.get('이름')]
            print(f"처리된 한국어 이름 {len(korean_names)}개")
            
            # 메모리 사용량 최적화를 위한 지연 처리
            yield chunk

# 메모리 매핑을 이용한 대용량 텍스트 처리
def search_in_large_korean_file(file_path, search_term):
    """메모리 매핑으로 대용량 한글 파일 검색"""
    with open(file_path, 'rb') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_file:
            # 한글 검색어를 바이트로 변환
            search_bytes = search_term.encode('utf-8')
            
            position = 0
            matches = []
            
            while True:
                position = mmapped_file.find(search_bytes, position)
                if position == -1:
                    break
                
                matches.append(position)
                position += 1
            
            return len(matches)

# ---- 원고 1222줄 ----
from functools import lru_cache, wraps
import time
from typing import Dict, Any

class KoreanDataCache:
    """한국어 데이터 전용 캐시 시스템"""
    
    def __init__(self, maxsize=128):
        self._cache = {}
        self._maxsize = maxsize
        self._stats = {'hits': 0, 'misses': 0}
    
    def get(self, key: str) -> Any:
        """캐시에서 데이터 조회"""
        if key in self._cache:
            self._stats['hits'] += 1
            return self._cache[key]
        
        self._stats['misses'] += 1
        return None
    
    def set(self, key: str, value: Any) -> None:
        """캐시에 데이터 저장"""
        if len(self._cache) >= self._maxsize:
            # 가장 먼저 넣은 항목을 지워 공간 확보
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        self._cache[key] = value
    
    def stats(self) -> Dict[str, int]:
        """캐시 통계 반환"""
        return self._stats.copy()

# 성능 측정 데코레이터
def measure_korean_performance(func):
    """함수 실행 성능을 측정하는 한국어 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.perf_counter() - start_time
            
            print(f"[성능] {func.__name__}: {execution_time:.4f}초 소요")
            return result
            
        except Exception as e:
            execution_time = time.perf_counter() - start_time
            print(f"[오류] {func.__name__}: {execution_time:.4f}초 후 실패 - {e}")
            raise
    
    return wrapper

@lru_cache(maxsize=256)
@measure_korean_performance
def expensive_korean_calculation(korean_text: str) -> int:
    """비용이 많이 드는 한국어 계산 (캐싱 적용)"""
    time.sleep(0.1)  # 무거운 계산 시뮬레이션
    
    # 한글 음절 수 계산
    korean_syllables = len([char for char in korean_text if '가' <= char <= '힣'])
    return korean_syllables * 1000

# 사용 예제
result1 = expensive_korean_calculation("안녕하세요 파이썬!")  # 첫 호출 (느림)
result2 = expensive_korean_calculation("안녕하세요 파이썬!")  # 캐시된 결과 (빠름)

# ---- 원고 1305줄 ----
import asyncio
import aiohttp
import aiofiles
from concurrent.futures import ThreadPoolExecutor
from typing import List

class AsyncKoreanDataProcessor:
    """비동기 한국어 데이터 처리 클래스"""
    
    def __init__(self, max_workers=5):
        self.session = None
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        self.executor.shutdown(wait=True)
    
    async def fetch_korean_news(self, urls: List[str]) -> List[str]:
        """여러 한국 뉴스 사이트에서 동시에 데이터 수집"""
        async def fetch_single(url):
            try:
                async with self.session.get(url) as response:
                    content = await response.text(encoding='utf-8')
                    return f"{url}: {len(content)}바이트 수집"
            except Exception as e:
                return f"{url}: 오류 - {str(e)}"
        
        tasks = [fetch_single(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    
    async def process_korean_files(self, file_paths: List[str]) -> List[str]:
        """여러 한국어 파일을 비동기로 처리"""
        async def process_file(path):
            try:
                async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    korean_chars = len([c for c in content if '가' <= c <= '힣'])
                    return f"{path}: 한글 {korean_chars}자"
            except Exception as e:
                return f"{path}: 오류 - {str(e)}"
        
        tasks = [process_file(path) for path in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    
    async def cpu_intensive_korean_analysis(self, texts: List[str]) -> List[dict]:
        """CPU 집약적인 한국어 분석을 비동기로 처리"""
        loop = asyncio.get_event_loop()
        
        def analyze_text(text):
            # CPU 집약적 작업은 스레드풀에서 실행
            korean_count = len([c for c in text if '가' <= c <= '힣'])
            word_count = len(text.split())
            complexity = korean_count * word_count
            
            return {
                'text_preview': text[:20] + '...' if len(text) > 20 else text,
                'korean_chars': korean_count,
                'words': word_count,
                'complexity': complexity
            }
        
        # CPU 작업을 스레드풀에서 병렬 실행
        tasks = [
            loop.run_in_executor(self.executor, analyze_text, text)
            for text in texts
        ]
        
        results = await asyncio.gather(*tasks)
        return results

# 사용 예제
async def main_async_example():
    korean_texts = [
        "파이썬은 훌륭한 프로그래밍 언어입니다.",
        "한국에서 파이썬 개발자가 늘어나고 있습니다.",
        "데이터 분석과 인공지능 분야에서 파이썬이 인기입니다."
    ]
    
    async with AsyncKoreanDataProcessor() as processor:
        # CPU 집약적 분석을 비동기로 실행
        analysis_results = await processor.cpu_intensive_korean_analysis(korean_texts)
        
        for result in analysis_results:
            print(f"텍스트: {result['text_preview']}")
            print(f"한글: {result['korean_chars']}자, 단어: {result['words']}개")
            print(f"복잡도: {result['complexity']}")
            print()

# asyncio.run(main_async_example())  # 주석 해제하여 실행

# ---- 원고 1416줄 ----
import logging
import time
from contextlib import contextmanager
from typing import Optional, Type, Callable
import traceback
from functools import wraps

class KoreanErrorHandler:
    """한국어 에러 처리 시스템"""
    
    def __init__(self, logger_name='한국_에러_처리'):
        self.logger = logging.getLogger(logger_name)
        self.setup_logger()
    
    def setup_logger(self):
        """한국어 로거 설정"""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def handle_korean_error(self, operation: str, error: Exception):
        """한국어 에러 메시지 처리"""
        error_messages = {
            FileNotFoundError: "파일을 찾을 수 없습니다",
            PermissionError: "권한이 없습니다",
            ValueError: "잘못된 값입니다",
            TypeError: "타입 오류입니다",
            KeyError: "키를 찾을 수 없습니다",
            UnicodeDecodeError: "한글 인코딩 오류입니다"
        }
        
        error_type = type(error)
        korean_msg = error_messages.get(error_type, "알 수 없는 오류입니다")
        
        self.logger.error(f"{operation} 중 {korean_msg}: {str(error)}")
        self.logger.debug(f"상세 오류:\n{traceback.format_exc()}")
    
    @contextmanager
    def safe_korean_operation(self, operation_name: str):
        """안전한 한국어 작업 컨텍스트 매니저"""
        try:
            self.logger.info(f"{operation_name} 시작")
            yield
            self.logger.info(f"{operation_name} 성공적으로 완료")
        except Exception as e:
            self.handle_korean_error(operation_name, e)
            raise
    
    def retry_korean_operation(self, max_attempts=3, delay=1.0):
        """한국어 작업 재시도 데코레이터"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_attempts):
                    try:
                        if attempt > 0:
                            time.sleep(delay)
                            self.logger.info(f"{func.__name__} {attempt + 1}번째 재시도")
                        
                        return func(*args, **kwargs)
                        
                    except Exception as e:
                        last_exception = e
                        self.logger.warning(f"{func.__name__} {attempt + 1}번째 시도 실패: {str(e)}")
                
                self.handle_korean_error(f"{func.__name__} 최종", last_exception)
                raise last_exception
            
            return wrapper
        return decorator

# 사용 예제
error_handler = KoreanErrorHandler()

@error_handler.retry_korean_operation(max_attempts=3, delay=0.5)
def unreliable_korean_function():
    """불안정한 한국어 처리 함수"""
    import random
    if random.random() < 0.7:  # 70% 확률로 실패
        raise ValueError("임의의 한글 처리 오류")
    return "한글 처리 성공!"

# 안전한 파일 처리 예제
def safe_korean_file_processing():
    with error_handler.safe_korean_operation("한글 파일 처리"):
        korean_content = "안녕하세요 파이썬!"
        
        # 파일 쓰기
        with open("테스트_한글.txt", "w", encoding="utf-8") as f:
            f.write(korean_content)
        
        # 파일 읽기
        with open("테스트_한글.txt", "r", encoding="utf-8") as f:
            content = f.read()
            print(f"읽은 내용: {content}")

# ---- 원고 1535줄 ----
import os
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from configparser import ConfigParser

@dataclass
class KoreanAppConfig:
    """한국어 앱 설정 클래스"""
    
    # 기본 설정
    app_name: str = "한국_파이썬_앱"
    version: str = "1.0.0"
    debug: bool = False
    
    # 데이터베이스 설정
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "korean_db"
    db_user: str = "postgres"
    db_password: str = ""
    
    # 로깅 설정
    log_level: str = "INFO"
    log_file: str = "한국_앱.log"
    
    # 한국어 설정
    locale: str = "ko_KR.UTF-8"
    timezone: str = "Asia/Seoul"
    date_format: str = "%Y년 %m월 %d일"
    
    # API 설정
    api_keys: Dict[str, str] = field(default_factory=dict)
    external_apis: Dict[str, str] = field(default_factory=lambda: {
        "weather": "https://api.openweathermap.org/data/2.5",
        "news": "https://newsapi.org/v2",
        "translate": "https://openapi.naver.com/v1/papago"
    })

class KoreanConfigManager:
    """한국어 설정 관리자"""
    
    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or Path("config")
        self.config_dir.mkdir(exist_ok=True)
        
        self.environments = ["development", "testing", "production"]
        self.current_env = os.environ.get("KOREAN_ENV", "development")
    
    def load_config(self, env: Optional[str] = None) -> KoreanAppConfig:
        """환경별 설정 로드"""
        env = env or self.current_env
        
        # 기본 설정으로 시작
        config = KoreanAppConfig()
        
        # 환경별 JSON 설정 파일 로드
        config_file = self.config_dir / f"{env}.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
                for key, value in config_data.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
        
        # 환경변수로 오버라이드
        self._override_with_env_vars(config)
        
        return config
    
    def save_config(self, config: KoreanAppConfig, env: str):
        """설정을 파일로 저장"""
        config_file = self.config_dir / f"{env}.json"
        config_dict = {
            key: getattr(config, key)
            for key in dir(config)
            if not key.startswith('_')
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, ensure_ascii=False, indent=2)
    
    def _override_with_env_vars(self, config: KoreanAppConfig):
        """환경변수로 설정 오버라이드"""
        env_mappings = {
            'KOREAN_DEBUG': ('debug', lambda x: x.lower() == 'true'),
            'KOREAN_DB_HOST': ('db_host', str),
            'KOREAN_DB_PORT': ('db_port', int),
            'KOREAN_LOG_LEVEL': ('log_level', str),
            'KOREAN_LOCALE': ('locale', str)
        }
        
        for env_var, (config_attr, converter) in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                try:
                    setattr(config, config_attr, converter(value))
                except (ValueError, TypeError) as e:
                    print(f"환경변수 {env_var} 변환 실패: {e}")

# 사용 예제
config_manager = KoreanConfigManager()

# 개발 환경 설정 로드
dev_config = config_manager.load_config("development")
print(f"앱 이름: {dev_config.app_name}")
print(f"디버그 모드: {dev_config.debug}")
print(f"타임존: {dev_config.timezone}")
