# [1권 Chapter 14: 모듈과 패키지 · 14.10 실전 프로젝트 구조 · manuscript/chapters/14-modules-packages.md:1938]
# src/seoul_food_platform/config/database.py
"""데이터베이스 연결 설정"""
from dataclasses import dataclass

from .settings import Settings


@dataclass(frozen=True)
class DatabaseConfig:
    """데이터베이스 연결에 필요한 값만 모은 설정"""
    url: str
    echo: bool = False      # True면 실행하는 SQL을 로그로 출력
    pool_size: int = 5      # 동시에 열어 둘 연결 수

    @property
    def is_sqlite(self) -> bool:
        """SQLite 데이터베이스인지 여부"""
        return self.url.startswith("sqlite://")

    @classmethod
    def from_settings(cls, settings: Settings) -> "DatabaseConfig":
        """애플리케이션 설정에서 데이터베이스 설정을 만든다"""
        return cls(url=settings.database_url, echo=settings.debug)
