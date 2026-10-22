# [1권 Chapter 14: 모듈과 패키지 · 14.10 실전 프로젝트 구조 · manuscript/chapters/14-modules-packages.md:1811]
# src/seoul_food_platform/config/settings.py
"""애플리케이션 설정"""
import os
from pathlib import Path
from typing import Optional, List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """애플리케이션 설정 클래스"""
    
    # 기본 설정
    app_name: str = "Seoul Food Platform"
    debug: bool = False
    version: str = "1.0.0"
    
    # 서버 설정
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # 데이터베이스 설정
    database_url: str = "postgresql://localhost:5432/seoul_food"
    redis_url: str = "redis://localhost:6379"
    
    # API 설정
    api_v1_prefix: str = "/api/v1"
    api_rate_limit: int = 1000
    api_timeout: int = 30
    
    # 보안 설정
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # 외부 API 키들
    google_maps_api_key: Optional[str] = None
    naver_api_key: Optional[str] = None
    kakao_api_key: Optional[str] = None
    
    # 로깅 설정
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # 파일 업로드 설정
    upload_directory: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: List[str] = [".jpg", ".jpeg", ".png", ".gif"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    @field_validator('database_url')
    @classmethod
    def validate_database_url(cls, v):
        """데이터베이스 URL 검증"""
        if not v.startswith(('postgresql://', 'sqlite://')):
            raise ValueError('지원하지 않는 데이터베이스 형식')
        return v
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        """로그 레벨 검증"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'로그 레벨은 {valid_levels} 중 하나여야 합니다')
        return v.upper()
    
    @property
    def upload_path(self) -> Path:
        """업로드 디렉토리 경로"""
        return Path(self.upload_directory)
    
    def create_upload_directory(self) -> None:
        """업로드 디렉토리 생성"""
        self.upload_path.mkdir(parents=True, exist_ok=True)

# 전역 설정 인스턴스
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """설정 인스턴스 반환 (싱글톤 패턴)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

# 환경별 설정 클래스들
class DevelopmentSettings(Settings):
    """개발 환경 설정"""
    debug: bool = True
    log_level: str = "DEBUG"
    database_url: str = "sqlite:///./dev.db"

class ProductionSettings(Settings):
    """운영 환경 설정"""
    debug: bool = False
    log_level: str = "WARNING"
    workers: int = 8

class TestSettings(Settings):
    """테스트 환경 설정"""
    debug: bool = True
    database_url: str = "sqlite:///./test.db"
    redis_url: str = "redis://localhost:6379/1"  # 다른 DB 사용

def get_settings_by_env(env: str = None) -> Settings:
    """환경에 따른 설정 반환"""
    env = env or os.getenv("ENVIRONMENT", "development")
    
    settings_map = {
        "development": DevelopmentSettings,
        "production": ProductionSettings,
        "testing": TestSettings
    }
    
    settings_class = settings_map.get(env, Settings)
    return settings_class()
