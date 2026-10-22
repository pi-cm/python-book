# [1권 Chapter 16: 메타프로그래밍과 고급 기법 · 6. 실전 프로젝트: 고급 ORM 시스템 · manuscript/chapters/16-metaprogramming-advanced.md:883]
# advanced_orm.py
from typing import Any, Dict, List, Optional
import sqlite3
import time
from contextlib import contextmanager
from functools import wraps

import pytest

class Field:
    """필드 디스크립터"""
    def __init__(self, field_type, null=True, default=None):
        self.field_type = field_type
        self.null = null
        self.default = default
        self.name = None
    
    def __set_name__(self, owner, name):
        self.name = name
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj._data.get(self.name, self.default)
    
    def __set__(self, obj, value):
        if value is None and not self.null:
            raise ValueError(f"{self.name}은 NULL이 될 수 없습니다")
        if value is not None and not isinstance(value, self.field_type):
            raise TypeError(f"{self.name}은 {self.field_type.__name__} 타입이어야 합니다")
        obj._data[self.name] = value

class ModelMeta(type):
    """모델 메타클래스"""
    def __new__(mcs, name, bases, namespace):
        if name == 'Model':
            return super().__new__(mcs, name, bases, namespace)
        
        # 필드 수집
        fields = {}
        for key, value in namespace.items():
            if isinstance(value, Field):
                fields[key] = value
        
        namespace['_fields'] = fields
        namespace['_table_name'] = name.lower()
        
        # 쿼리 메서드 자동 추가
        def save(self):
            columns = ', '.join(self._fields.keys())
            placeholders = ', '.join(['?' for _ in self._fields])
            values = [getattr(self, field) for field in self._fields]
            
            query = f"INSERT INTO {self._table_name} ({columns}) VALUES ({placeholders})"
            return query, values
        
        namespace['save'] = save
        
        return super().__new__(mcs, name, bases, namespace)

class Model(metaclass=ModelMeta):
    """베이스 모델 클래스"""
    def __init__(self, **kwargs):
        self._data = {}
        for field_name in self._fields:
            if field_name in kwargs:
                setattr(self, field_name, kwargs[field_name])

@contextmanager
def database_transaction():
    """데이터베이스 트랜잭션 컨텍스트 매니저"""
    conn = sqlite3.connect(':memory:')
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def timing_decorator(func):
    """실행 시간 측정 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 실행 시간: {end - start:.4f}초")
        return result
    return wrapper

# 사용 예제
class 사용자(Model):
    이름 = Field(str, null=False)
    이메일 = Field(str, null=False)
    나이 = Field(int, default=0)

class TestAdvancedORM:
    def test_orm_system(self):
        """고급 ORM 시스템 테스트"""
        # 모델 생성
        user = 사용자(이름="김철수", 이메일="kim@example.com", 나이=30)
        
        # 필드 접근
        assert user.이름 == "김철수"
        assert user.이메일 == "kim@example.com"
        assert user.나이 == 30
        
        # 타입 검증
        with pytest.raises(TypeError):
            user.나이 = "서른"
        
        # NULL 검증
        with pytest.raises(ValueError):
            user.이름 = None
        
        # 쿼리 생성
        query, values = user.save()
        expected_query = "INSERT INTO 사용자 (이름, 이메일, 나이) VALUES (?, ?, ?)"
        assert query == expected_query
        assert values == ["김철수", "kim@example.com", 30]
        
        # 트랜잭션 테스트
        with database_transaction() as conn:
            conn.execute('''
                CREATE TABLE 사용자 (
                    이름 TEXT NOT NULL,
                    이메일 TEXT NOT NULL,
                    나이 INTEGER DEFAULT 0
                )
            ''')
            
            conn.execute(query, values)
            
            cursor = conn.execute("SELECT * FROM 사용자")
            row = cursor.fetchone()
            assert row == ("김철수", "kim@example.com", 30)

if __name__ == "__main__":
    # 실제 사용 예제
    user = 사용자(이름="박영희", 이메일="park@example.com")
    print(f"사용자: {user.이름}, 이메일: {user.이메일}")
    
    query, values = user.save()
    print(f"쿼리: {query}")
    print(f"값들: {values}")
