# [1권 Chapter 14: 모듈과 패키지 · 14.10 실전 프로젝트 구조 · manuscript/chapters/14-modules-packages.md:1970]
# src/seoul_food_platform/models/base.py
"""기본 모델 클래스"""
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from uuid import uuid4, UUID

@dataclass
class BaseModel:
    """모든 모델의 기본 클래스"""
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    
    def __post_init__(self):
        """초기화 후 처리"""
        if isinstance(self.id, str):
            self.id = UUID(self.id)
    
    def update_timestamp(self):
        """수정 시간 업데이트"""
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, UUID):
                result[key] = str(value)
            else:
                result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """딕셔너리에서 객체 생성"""
        # datetime 필드 변환
        for field_name in ['created_at', 'updated_at']:
            if field_name in data and isinstance(data[field_name], str):
                data[field_name] = datetime.fromisoformat(data[field_name])
        
        # UUID 필드 변환
        if 'id' in data and isinstance(data['id'], str):
            data['id'] = UUID(data['id'])
        
        return cls(**data)

@dataclass
class TimestampMixin:
    """타임스탬프 믹스인"""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def touch(self):
        """수정 시간 업데이트"""
        self.updated_at = datetime.now()

@dataclass  
class SoftDeleteMixin:
    """소프트 삭제 믹스인"""
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    
    def delete(self):
        """소프트 삭제"""
        self.is_deleted = True
        self.deleted_at = datetime.now()
    
    def restore(self):
        """삭제 복원"""
        self.is_deleted = False
        self.deleted_at = None
