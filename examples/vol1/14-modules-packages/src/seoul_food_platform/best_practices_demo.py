# [1권 Chapter 14: 모듈과 패키지 · 정리 및 베스트 프랙티스 · manuscript/chapters/14-modules-packages.md:2844]
# src/seoul_food_platform/best_practices_demo.py
# 패키지 안 모듈이라 실행은: uv run python -m seoul_food_platform.best_practices_demo
"""모듈과 패키지 베스트 프랙티스"""

# 1. Import 순서 (PEP 8)
# 표준 라이브러리
import os
import sys
from pathlib import Path
from typing import List, Dict

# 외부 라이브러리 (이 파일은 쓰지 않아 비워 둠 — 쓰지 않는 import는 넣지 않는다)

# 로컬 애플리케이션 (같은 패키지 안의 모듈)
from .services.restaurant_service import RestaurantService

# 2. __all__ 사용하여 public API 명시
__all__ = ['RestaurantManager', 'setup_logging']

# 3. 모듈 레벨 상수
DEFAULT_CONFIG_FILE = Path.home() / '.seoul-food' / 'config.json'
MAX_RETRY_ATTEMPTS = 3

# 4. 모듈 초기화 함수
def setup_logging(level: str = 'INFO'):
    """로깅 설정"""
    import logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# 5. 메인 클래스
class RestaurantManager:
    """레스토랑 관리자 - 모듈의 메인 인터페이스"""
    
    def __init__(self, config_file: Path = DEFAULT_CONFIG_FILE):
        self.config_file = config_file
        self.service = RestaurantService()
        self._load_config()
    
    def _load_config(self):
        """설정 로드 (private 메서드)"""
        if self.config_file.exists():
            # 설정 로드 로직
            pass

# 6. 모듈이 직접 실행될 때의 동작
if __name__ == '__main__':
    # 간단한 테스트나 유틸리티 실행
    setup_logging('DEBUG')
    manager = RestaurantManager()
    print("레스토랑 관리자가 초기화되었습니다.")
