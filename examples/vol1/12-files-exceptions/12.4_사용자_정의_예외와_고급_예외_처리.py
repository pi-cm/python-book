"""1권 Chapter 12: 파일과 예외 처리 — 12.4 사용자 정의 예외와 고급 예외 처리

원고: manuscript/chapters/12-files-exceptions.md (879줄부터)
"""

# ---- 원고 879줄 ----
from typing import Optional, Dict, Any
from datetime import datetime
import logging

# 한국어 예외 클래스 정의
class KoreanError(Exception):
    """한국어 관련 기본 예외 클래스"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "GENERAL_ERROR"
        self.context = context or {}
        self.timestamp = datetime.now()
    
    def __str__(self):
        return f"[{self.error_code}] {self.message}"
    
    def to_dict(self):
        """예외 정보를 딕셔너리로 반환"""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
            "timestamp": self.timestamp.isoformat()
        }

class KoreanValidationError(KoreanError):
    """한국어 데이터 검증 오류"""
    
    def __init__(self, field_name: str, value: Any, message: str):
        context = {"field": field_name, "value": str(value)}
        super().__init__(message, "VALIDATION_ERROR", context)
        self.field_name = field_name
        self.value = value

class KoreanPhoneNumberError(KoreanValidationError):
    """한국 전화번호 형식 오류"""
    
    def __init__(self, phone_number: str):
        message = f"올바르지 않은 한국 전화번호 형식: {phone_number} (예: 010-1234-5678)"
        super().__init__("phone_number", phone_number, message)

class KoreanBusinessNumberError(KoreanValidationError):
    """한국 사업자등록번호 형식 오류"""
    
    def __init__(self, business_number: str):
        message = f"올바르지 않은 사업자등록번호 형식: {business_number} (예: 123-45-67891)"
        super().__init__("business_number", business_number, message)

class KoreanNameError(KoreanValidationError):
    """한국 이름 형식 오류"""
    
    def __init__(self, name: str, reason: str = "한글 2-5글자여야 합니다"):
        message = f"올바르지 않은 한국 이름: {name} ({reason})"
        super().__init__("korean_name", name, message)

# 한국 데이터 검증 클래스
class KoreanDataValidator:
    """한국 데이터 검증기"""
    
    @staticmethod
    def validate_phone_number(phone: str) -> str:
        """한국 전화번호 검증"""
        import re
        
        # 하이픈 제거 후 검증
        cleaned_phone = re.sub(r'[-\s]', '', phone)
        
        # 010으로 시작하는 11자리 숫자
        if not re.match(r'^010\d{8}$', cleaned_phone):
            raise KoreanPhoneNumberError(phone)
        
        # 표준 형식으로 반환
        return f"{cleaned_phone[:3]}-{cleaned_phone[3:7]}-{cleaned_phone[7:]}"
    
    @staticmethod  
    def validate_business_number(business_num: str) -> str:
        """사업자등록번호 검증"""
        import re
        
        # 하이픈 제거
        cleaned_num = re.sub(r'[-\s]', '', business_num)
        
        # 10자리 숫자 검증
        if not re.match(r'^\d{10}$', cleaned_num):
            raise KoreanBusinessNumberError(business_num)
        
        # 체크섬 검증 (사업자등록번호 검증 규칙)
        check_digits = [1, 3, 7, 1, 3, 7, 1, 3, 5]
        total = sum(int(cleaned_num[i]) * check_digits[i] for i in range(9))
        total += int(cleaned_num[8]) * 5 // 10  # 9번째 자리 × 5의 십의 자리를 한 번 더 더함
        check_digit = (10 - (total % 10)) % 10
        
        if int(cleaned_num[9]) != check_digit:
            raise KoreanBusinessNumberError(business_num)
        
        # 표준 형식으로 반환
        return f"{cleaned_num[:3]}-{cleaned_num[3:5]}-{cleaned_num[5:]}"
    
    @staticmethod
    def validate_korean_name(name: str) -> str:
        """한국 이름 검증"""
        import re
        
        # 한글만 허용, 2-5글자
        if not re.match(r'^[가-힣]{2,5}$', name):
            if not re.match(r'^[가-힣]+$', name):
                reason = "한글만 입력 가능합니다"
            elif len(name) < 2:
                reason = "최소 2글자 이상이어야 합니다" 
            elif len(name) > 5:
                reason = "최대 5글자까지 가능합니다"
            else:
                reason = "올바르지 않은 형식입니다"
            
            raise KoreanNameError(name, reason)
        
        return name

def demonstrate_custom_exceptions():
    """사용자 정의 예외 시연"""
    
    print("=== 사용자 정의 예외 시연 ===")
    
    # 테스트 데이터
    test_data = [
        {"type": "phone", "value": "010-1234-5678", "valid": True},
        {"type": "phone", "value": "010-1234-567", "valid": False},   # 숫자가 10자리
        {"type": "phone", "value": "011-1234-5678", "valid": False},
        {"type": "business", "value": "123-45-67890", "valid": False},  # 체크섬 오류
        {"type": "business", "value": "123-45-67891", "valid": True},   # 체크섬이 맞는 번호
        {"type": "name", "value": "김철수", "valid": True},
        {"type": "name", "value": "김", "valid": False},
        {"type": "name", "value": "Kim철수", "valid": False},
    ]
    
    validator = KoreanDataValidator()
    
    for data in test_data:
        try:
            if data["type"] == "phone":
                result = validator.validate_phone_number(data["value"])
                print(f"[O] 전화번호 검증 성공: {data['value']} → {result}")
            
            elif data["type"] == "business":
                result = validator.validate_business_number(data["value"])
                print(f"[O] 사업자번호 검증 성공: {data['value']} → {result}")
            
            elif data["type"] == "name":
                result = validator.validate_korean_name(data["value"])
                print(f"[O] 이름 검증 성공: {data['value']}")
                
        except KoreanError as e:
            expected = "[X]" if not data["valid"] else "[!]"
            print(f"{expected} {e}")
            
            # 예외 상세 정보
            if not data["valid"]:  # 예상된 오류인 경우 상세 정보 표시
                error_dict = e.to_dict()
                print(f"   오류 정보: {error_dict}")

# 예외 체이닝과 재발생
def exception_chaining_demo():
    """예외 체이닝 시연"""
    
    print("\n=== 예외 체이닝 시연 ===")
    
    def process_korean_user_data(user_data: dict):
        """한국 사용자 데이터 처리"""
        try:
            # 이름 검증
            name = KoreanDataValidator.validate_korean_name(user_data.get("name", ""))
            
            # 전화번호 검증
            phone = KoreanDataValidator.validate_phone_number(user_data.get("phone", ""))
            
            # 사업자번호 검증 (있는 경우)
            business_num = user_data.get("business_number")
            if business_num:
                business_num = KoreanDataValidator.validate_business_number(business_num)
            
            return {
                "name": name,
                "phone": phone,
                "business_number": business_num,
                "status": "validated"
            }
            
        except KoreanValidationError as validation_error:
            # 원본 예외를 체인으로 연결하여 새 예외 발생
            raise KoreanError(
                f"사용자 데이터 검증 실패: {user_data.get('name', 'Unknown')}",
                "USER_DATA_VALIDATION_FAILED",
                {"user_data": user_data}
            ) from validation_error
    
    # 테스트 데이터
    test_users = [
        {"name": "김철수", "phone": "010-1234-5678"},  # 정상
        {"name": "이", "phone": "010-1234-5678"},      # 이름 오류
        {"name": "박민수", "phone": "010-1234-567"},    # 전화번호 오류
    ]
    
    for user in test_users:
        try:
            result = process_korean_user_data(user)
            print(f"[O] 사용자 데이터 처리 성공: {result['name']}")
        
        except KoreanError as e:
            print(f"[X] 사용자 데이터 처리 실패: {e}")
            
            # 원본 예외 확인 (__cause__ 속성)
            if e.__cause__:
                print(f"   원인: {e.__cause__}")
                print(f"   원인 타입: {type(e.__cause__).__name__}")

# 로깅과 함께하는 예외 처리
def logging_with_exceptions():
    """로깅과 함께하는 예외 처리"""
    
    print("\n=== 로깅과 예외 처리 ===")
    
    # 로거 설정
    logger = logging.getLogger("korean_app")
    logger.setLevel(logging.DEBUG)
    
    # 콘솔 핸들러
    if not logger.handlers:  # 중복 핸들러 방지
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    def secure_korean_data_processor(data: dict):
        """보안이 중요한 한국 데이터 처리기"""
        
        logger.info(f"데이터 처리 시작: {data.get('name', 'Unknown')}")
        
        try:
            # 민감한 개인정보 처리 시뮬레이션
            if "ssn" in data:  # 주민등록번호
                logger.warning("주민등록번호 처리 - 보안 검사 필요")
                # 실제로는 암호화 등의 보안 처리
            
            # 데이터 검증
            validated_data = {}
            validated_data["name"] = KoreanDataValidator.validate_korean_name(data["name"])
            validated_data["phone"] = KoreanDataValidator.validate_phone_number(data["phone"])
            
            logger.info(f"데이터 검증 완료: {validated_data['name']}")
            return validated_data
            
        except KoreanValidationError as e:
            # 검증 오류는 WARNING 레벨
            logger.warning(f"데이터 검증 실패: {e}", exc_info=True)
            raise
            
        except Exception as e:
            # 예상치 못한 오류는 ERROR 레벨
            logger.error(f"예상치 못한 오류 발생", exc_info=True)
            
            # 민감한 정보가 포함된 데이터는 로그에서 제외
            safe_data = {k: v for k, v in data.items() if k not in ["ssn", "password"]}
            logger.error(f"처리 중이던 안전한 데이터: {safe_data}")
            
            raise KoreanError(
                "시스템 오류가 발생했습니다. 관리자에게 문의하세요.",
                "SYSTEM_ERROR",
                {"timestamp": datetime.now().isoformat()}
            ) from e
    
    # 테스트
    test_cases = [
        {"name": "김철수", "phone": "010-1234-5678"},
        {"name": "이영희", "phone": "010-1234-5678", "ssn": "123456-1234567"},
        {"name": "박", "phone": "010-1234-5678"},  # 이름 오류
    ]
    
    for case in test_cases:
        try:
            result = secure_korean_data_processor(case)
            print(f"[O] 처리 완료: {result}")
        except KoreanError as e:
            print(f"[X] 처리 실패: {e}")

# 실행
demonstrate_custom_exceptions()
exception_chaining_demo()
logging_with_exceptions()
