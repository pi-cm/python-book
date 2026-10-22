"""1권 Chapter 17: 표준 라이브러리 핵심 가이드 — 로깅과 디버깅

원고: manuscript/chapters/17-standard-library-guide.md (803줄부터)
"""

# ---- 원고 803줄 ----
import logging
import traceback
from datetime import datetime

# 한국어 로거 설정
def setup_korean_logger():
    logger = logging.getLogger('한국_서비스')
    logger.setLevel(logging.DEBUG)
    
    # 파일 핸들러 (한글 지원)
    file_handler = logging.FileHandler('서비스_로그.log', encoding='utf-8')
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    
    # 한국어 포맷터
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_korean_logger()

# 한국어 로그 메시지
def korean_login(username):
    try:
        logger.info(f"사용자 '{username}'님이 로그인을 시도합니다")
        
        # 실제 로그인 로직 (시뮬레이션)
        if username == "관리자":
            raise PermissionError("관리자 계정은 특별한 권한이 필요합니다")
        
        logger.info(f"사용자 '{username}'님 로그인 성공")
        return True
        
    except Exception as e:
        logger.error(f"로그인 오류 발생: {str(e)}")
        logger.debug(f"상세 오류 정보:\n{traceback.format_exc()}")
        return False

# 테스트
korean_login("김철수")
korean_login("관리자")

# 성능 로깅
import time
import functools

def performance_log(func):
    """함수 실행 시간을 로깅하는 데코레이터"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"'{func.__name__}' 함수 실행 시작")
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"'{func.__name__}' 함수 실행 완료 (소요시간: {execution_time:.3f}초)")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"'{func.__name__}' 함수 실행 실패 (소요시간: {execution_time:.3f}초): {str(e)}")
            raise
    
    return wrapper

@performance_log
def process_korean_data(data_size):
    """한국어 데이터 처리 시뮬레이션"""
    time.sleep(data_size * 0.001)  # 데이터 크기에 비례한 처리 시간
    return f"{data_size}건의 한국어 데이터 처리 완료"

# 성능 테스트
result = process_korean_data(1000)
print(result)
