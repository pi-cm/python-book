"""1권 Chapter 18: 데이터베이스 연동 — 18.10 보안 고려사항

원고: manuscript/chapters/18-database-integration.md (1811줄부터)
"""

# ---- 원고 1811줄 ----
from typing import Optional
import re

class DataValidator:
    """데이터 유효성 검증 클래스"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """이메일 형식을 검증합니다."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """전화번호 형식을 검증합니다."""
        # 한국 전화번호 패턴
        pattern = r'^01[016789]-?\d{3,4}-?\d{4}$'
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def validate_salary(salary: int) -> bool:
        """월급 범위를 검증합니다."""
        return 3000000 <= salary <= 20000000  # 300만원 ~ 2000만원
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """입력 텍스트를 정제합니다."""
        if not isinstance(text, str):
            return ""
        # 특수 문자 제거 및 공백 정리
        sanitized = re.sub(r'[<>"\']', '', text.strip())
        return sanitized

def add_employee_safe(name: str, department: str, position: str, 
                     salary: int, email: str, phone: Optional[str] = None):
    """안전한 직원 추가 함수"""
    
    validator = DataValidator()
    
    # 입력 검증
    if not name or len(name.strip()) < 2:
        raise ValueError("이름은 2글자 이상이어야 합니다.")
    
    if not validator.validate_email(email):
        raise ValueError("올바른 이메일 형식이 아닙니다.")
    
    if not validator.validate_salary(salary):
        raise ValueError("월급은 300만원 이상 2000만원 이하여야 합니다.")
    
    if phone and not validator.validate_phone(phone):
        raise ValueError("올바른 전화번호 형식이 아닙니다.")
    
    # 입력 데이터 정제
    name = validator.sanitize_input(name)
    department = validator.sanitize_input(department)
    position = validator.sanitize_input(position)
    
    # 데이터베이스에 저장
    with get_connection() as conn:
        try:
            conn.execute("""
                INSERT INTO employees (name, department, position, salary, hire_date, email)
                VALUES (?, ?, ?, ?, date('now'), ?)
            """, (name, department, position, salary, email))
            conn.commit()
            print(f"직원 {name}이 안전하게 추가되었습니다.")
            
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError("이미 존재하는 이메일 주소입니다.")
            else:
                raise ValueError(f"데이터베이스 제약 조건 오류: {e}")

# 안전한 직원 추가 테스트
try:
    add_employee_safe("테스트직원", "IT팀", "개발자", 5500000, "test.new@company.co.kr", "010-9999-8888")
except ValueError as e:
    print(f"검증 오류: {e}")
