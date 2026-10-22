"""1권 Chapter 8: 고급 데이터 구조 — 8.5 Pydantic을 활용한 현대적 데이터 검증

원고: manuscript/chapters/08-advanced-data-structures.md (862줄부터)
"""

# ---- 원고 862줄 ----
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing import List, Optional, Union
from datetime import date, datetime
import re
import json

# 기본 Pydantic 모델
class KoreanPerson(BaseModel):
    """한국인 개인정보 모델"""
    name: str = Field(..., min_length=2, max_length=10, description="한글 이름")
    age: int = Field(..., ge=0, le=120, description="나이")
    phone: str = Field(..., pattern=r'^010-\d{4}-\d{4}$', description="휴대폰 번호")
    email: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')
    birth_date: Optional[date] = None
    
    @field_validator('name')
    @classmethod
    def validate_korean_name(cls, v):
        """한글 이름 검증"""
        korean_pattern = re.compile(r'^[가-힣]{2,5}$')
        if not korean_pattern.match(v):
            raise ValueError('한글 2-5자로 입력해주세요')
        return v
    
    @model_validator(mode='after')
    def validate_birth_date(self):
        """생년월일과 나이의 일관성 검증"""
        if self.birth_date and self.age:
            calculated_age = datetime.now().year - self.birth_date.year
            if abs(calculated_age - self.age) > 1:
                raise ValueError('나이와 생년월일이 일치하지 않습니다')
        return self
    
    # JSON 스키마 생성 시 예시 데이터 포함
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "김철수",
                "age": 26,
                "phone": "010-1234-5678", 
                "email": "kim@example.com",
                "birth_date": "1998-03-15"
            }
        }
    )

# 자동 타입 변환 시연
def demonstrate_pydantic_basics():
    """Pydantic 기본 기능 시연"""
    print("Pydantic 기본 검증:")
    
    # 올바른 데이터
    try:
        person = KoreanPerson(
            name="김철수",
            age=26,
            phone="010-1234-5678",
            email="kim@example.com"
        )
        print(f"[O] 유효한 데이터: {person.name}, {person.age}세")
    except Exception as e:
        print(f"[X] 검증 실패: {e}")
    
    # 자동 타입 변환
    try:
        person = KoreanPerson(
            name="이영희",
            age="30",  # 문자열 -> 정수 자동 변환
            phone="010-9876-5432"
        )
        print(f"[O] 타입 변환: 나이 {person.age} (타입: {type(person.age)})")
    except Exception as e:
        print(f"[X] 변환 실패: {e}")
    
    # 검증 실패 사례
    try:
        invalid_person = KoreanPerson(
            name="Kim",  # 영문 이름
            age=26,
            phone="010-1234-567"  # 잘못된 번호 형식
        )
    except Exception as e:
        print(f"[X] 예상된 검증 실패: {e}")

demonstrate_pydantic_basics()

# ---- 원고 962줄 ----
class KoreanAddress(BaseModel):
    """한국 주소 검증 모델"""
    postal_code: str = Field(..., pattern=r'^\d{5}$', description="우편번호")
    city: str = Field(..., min_length=2, description="시/도")
    district: str = Field(..., min_length=2, description="구/군")
    street: str = Field(..., min_length=3, description="상세주소")
    
    @field_validator('city')
    @classmethod
    def validate_korean_city(cls, v):
        """한국 시/도명 검증"""
        valid_cities = [
            '서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시', 
            '대전광역시', '울산광역시', '세종특별자치시', '경기도', '강원도',
            '충청북도', '충청남도', '전라북도', '전라남도', '경상북도', '경상남도', '제주특별자치도'
        ]
        
        # 간단한 형태도 허용 (서울, 부산 등)
        simple_names = [city.replace('특별시', '').replace('광역시', '').replace('도', '') 
                       for city in valid_cities]
        
        if v not in valid_cities and v not in simple_names:
            raise ValueError(f'올바른 시/도명을 입력해주세요. 입력값: {v}')
        return v

class KoreanBusiness(BaseModel):
    """한국 사업자 정보 모델"""
    business_name: str = Field(..., min_length=2, max_length=50)
    business_number: str = Field(..., pattern=r'^\d{3}-\d{2}-\d{5}$', 
                                description="사업자등록번호 (123-45-67890)")
    address: KoreanAddress
    phone: str = Field(..., pattern=r'^0\d{1,2}-\d{3,4}-\d{4}$', 
                      description="사업장 전화번호")
    ceo_name: str = Field(..., description="대표자명")
    employees: int = Field(default=1, ge=1, le=10000, description="직원 수")
    
    @field_validator('business_number')
    @classmethod
    def validate_business_number(cls, v):
        """사업자등록번호 체크섬 검증"""
        # 간단한 체크섬 검증 (실제로는 더 복잡한 알고리즘 사용)
        digits = ''.join(c for c in v if c.isdigit())
        if len(digits) != 10:
            raise ValueError('사업자등록번호는 10자리 숫자여야 합니다')
        
        # 체크섬 계산 (간소화된 버전)
        multipliers = [1, 3, 7, 1, 3, 7, 1, 3, 5, 1]
        total = sum(int(digit) * mult for digit, mult in zip(digits, multipliers))
        
        if total % 10 != 0:
            # 실제 구현에서는 더 정확한 체크섬 사용
            print(f"[!] 사업자등록번호 체크섬 확인 필요: {v}")
        
        return v
    
    @model_validator(mode='after')
    def validate_business_logic(self):
        """사업자 정보 전체 검증"""
        if self.ceo_name and self.business_name:
            # CEO 이름이 사업자명과 동일한 경우 개인사업자로 간주
            if self.ceo_name in self.business_name:
                if self.employees > 50:
                    raise ValueError('개인사업자는 직원 수 제한이 있습니다')
        
        return self

class KoreanEmployee(BaseModel):
    """한국 직원 정보 모델"""
    personal_info: KoreanPerson
    employee_id: str = Field(..., pattern=r'^EMP\d{4}$')
    department: str = Field(..., min_length=2)
    position: str = Field(..., min_length=2)
    salary: int = Field(..., ge=2000000, le=200000000, description="연봉 (원)")
    hire_date: date = Field(default_factory=date.today)
    
    @field_validator('hire_date')
    @classmethod
    def validate_hire_date(cls, v):
        """입사일 검증"""
        if v > date.today():
            raise ValueError('입사일은 미래일 수 없습니다')
        if v.year < 1980:
            raise ValueError('입사일이 너무 과거입니다')
        return v
    
    def calculate_years_of_service(self) -> int:
        """근속년수 계산"""
        today = date.today()
        years = today.year - self.hire_date.year
        if today.month < self.hire_date.month or \
           (today.month == self.hire_date.month and today.day < self.hire_date.day):
            years -= 1
        return max(0, years)

# 한국 특화 검증 시연
def demonstrate_korean_validation():
    """한국 특화 데이터 검증 시연"""
    print("\n한국 특화 데이터 검증:")
    
    # 주소 검증
    address = KoreanAddress(
        postal_code="06234",
        city="서울",
        district="강남구",
        street="테헤란로 123"
    )
    print(f"[O] 주소: {address.city} {address.district} {address.street}")
    
    # 사업자 정보 검증
    try:
        business = KoreanBusiness(
            business_name="파이썬 테크놀로지",
            business_number="123-45-67890",
            address=address,
            phone="02-1234-5678",
            ceo_name="김대표",
            employees=15
        )
        print(f"[O] 사업자: {business.business_name} ({business.business_number})")
    except Exception as e:
        print(f"[X] 사업자 검증 실패: {e}")
    
    # 직원 정보 검증
    person = KoreanPerson(
        name="박개발",
        age=28,
        phone="010-1111-2222",
        email="park@company.com"
    )
    
    employee = KoreanEmployee(
        personal_info=person,
        employee_id="EMP0001",
        department="개발팀",
        position="시니어 개발자",
        salary=60000000,
        hire_date=date(2021, 3, 15)
    )
    
    years_service = employee.calculate_years_of_service()
    print(f"[O] 직원: {person.name}, 근속 {years_service}년")

demonstrate_korean_validation()

# ---- 원고 1120줄 ----
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, create_model
from typing import Dict, Any, Union, Literal
from enum import Enum

class PaymentMethod(str, Enum):
    """결제 수단"""
    CARD = "카드"
    CASH = "현금" 
    TRANSFER = "계좌이체"
    MOBILE = "모바일결제"

class OrderStatus(str, Enum):
    """주문 상태"""
    PENDING = "대기"
    CONFIRMED = "확인"
    SHIPPED = "배송중"
    DELIVERED = "배송완료"
    CANCELLED = "취소"

class KoreanOrder(BaseModel):
    """한국 전자상거래 주문 모델"""
    order_id: str = Field(..., pattern=r'^ORD\d{8}$')
    customer_name: str = Field(..., min_length=2, max_length=10)
    customer_phone: str = Field(..., pattern=r'^010-\d{4}-\d{4}$')
    
    # Union 타입으로 여러 결제 수단 지원
    payment_method: PaymentMethod
    payment_amount: int = Field(..., gt=0, description="결제금액")
    
    # Literal 타입으로 정확한 값 제한
    currency: Literal["KRW"] = "KRW"
    
    shipping_address: KoreanAddress
    status: OrderStatus = OrderStatus.PENDING
    
    # 선택적 필드들
    discount_rate: Optional[float] = Field(None, ge=0.0, le=0.5, description="할인율")
    notes: Optional[str] = Field(None, max_length=500)
    
    @model_validator(mode='after')
    def validate_order_logic(self):
        """주문 전체 로직 검증"""
        # 결제 방법별 한도 확인
        if self.payment_method == PaymentMethod.MOBILE and self.payment_amount > 1000000:
            raise ValueError('모바일결제는 일일 100만원 한도입니다')
        
        if self.payment_method == PaymentMethod.CASH and self.payment_amount > 5000000:
            raise ValueError('현금결제는 500만원 한도입니다')
        
        # 할인이 적용된 경우 최소 금액 확인
        if self.discount_rate and self.payment_amount:
            if self.payment_amount < 10000:
                raise ValueError('할인 적용 시 최소 주문금액은 1만원입니다')
        
        # 배송지와 고객 정보 일관성 확인
        if self.shipping_address and self.customer_name:
            # 서울 지역 당일배송 최소 금액
            if (self.shipping_address.city in ['서울', '서울특별시'] and 
                self.payment_amount < 30000):
                current_notes = self.notes or ''
                self.notes = (current_notes + ' [당일배송 최소금액 미달]').strip()
        
        return self
    
    def calculate_final_amount(self) -> int:
        """최종 결제 금액 계산"""
        if self.discount_rate:
            return int(self.payment_amount * (1 - self.discount_rate))
        return self.payment_amount
    
    def can_cancel(self) -> bool:
        """취소 가능 여부"""
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]

# 동적 모델 생성 (런타임 모델)
def create_survey_model(questions: Dict[str, str]) -> type[BaseModel]:
    """설문조사 동적 모델 생성"""
    fields = {}
    
    for field_name, question in questions.items():
        if '점수' in question:
            fields[field_name] = (int, Field(..., ge=1, le=10, description=question))
        elif '이메일' in question:
            fields[field_name] = (str, Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$', description=question))
        else:
            fields[field_name] = (str, Field(..., min_length=1, max_length=200, description=question))
    
    return create_model('DynamicSurvey', **fields)

# model_config 고급 설정
class KoreanProduct(BaseModel):
    """한국 상품 정보"""
    name: str = Field(..., min_length=2, max_length=100)
    price: int = Field(..., gt=0)
    category: str
    made_in_korea: bool = True
    
    model_config = ConfigDict(
        # 추가 속성 허용 안함
        extra="forbid",
        
        # 검증 전에 문자열 앞뒤 공백 제거
        str_strip_whitespace=True,
        
        # 스키마 예제
        json_schema_extra={
            "example": {
                "name": "한국산 김치",
                "price": 15000,
                "category": "식품",
                "made_in_korea": True
            }
        }
    )

# 고급 기능 시연
def demonstrate_advanced_pydantic():
    """고급 Pydantic 기능 시연"""
    print("\n고급 Pydantic 기능:")
    
    # 복잡한 주문 검증
    address = KoreanAddress(
        postal_code="12345",
        city="서울",
        district="강남구", 
        street="테헤란로 456"
    )
    
    order = KoreanOrder(
        order_id="ORD20231201",
        customer_name="최고객",
        customer_phone="010-9999-8888",
        payment_method=PaymentMethod.CARD,
        payment_amount=50000,
        shipping_address=address,
        discount_rate=0.1
    )
    
    final_amount = order.calculate_final_amount()
    print(f"[O] 주문: {order.order_id}, 최종금액: {final_amount:,}원")
    print(f"   취소가능: {order.can_cancel()}")
    
    # 동적 모델 생성
    survey_questions = {
        "satisfaction_score": "서비스 만족도 점수는?",
        "email": "이메일 주소를 입력하세요",
        "feedback": "추가 의견이 있으시면 작성해주세요"
    }
    
    SurveyModel = create_survey_model(survey_questions)
    
    survey = SurveyModel(
        satisfaction_score=9,
        email="customer@example.com",
        feedback="서비스가 매우 좋습니다"
    )
    
    print(f"[O] 설문조사: 만족도 {survey.satisfaction_score}점")
    
    # 상품 정보
    product = KoreanProduct(
        name="  한국산 고추장  ",  # 공백 자동 제거
        price=8000,
        category="조미료"
    )
    
    print(f"[O] 상품: {product.name} ({product.price:,}원)")

demonstrate_advanced_pydantic()

# ---- 원고 1308줄 ----
from pydantic import BaseModel
from typing import List, Dict
import json
from fastapi import FastAPI
from datetime import datetime

class APIResponse(BaseModel):
    """표준 API 응답 형식"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)  # JSON에서는 ISO 형식 문자열로 바뀜

class KoreanUserAPI(BaseModel):
    """API용 한국 사용자 모델"""
    user_id: str = Field(..., pattern=r'^USER\d{6}$')
    name: str = Field(..., min_length=2, max_length=10)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    phone: str = Field(..., pattern=r'^010-\d{4}-\d{4}$')
    address: KoreanAddress
    preferences: Dict[str, Any] = Field(default_factory=dict)
    
    def to_api_response(self, message: str = "성공") -> APIResponse:
        """API 응답 형식으로 변환"""
        return APIResponse(
            success=True,
            message=message,
            data=self.model_dump()
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'KoreanUserAPI':
        """JSON 문자열에서 객체 생성"""
        data = json.loads(json_str)
        return cls(**data)
    
    def to_json(self) -> str:
        """JSON 문자열로 변환"""
        return self.model_dump_json(indent=2)

# OpenAPI 스키마 생성을 위한 FastAPI 통합 예제
app = FastAPI(title="Korean User API", version="1.0.0")

@app.post("/users/", response_model=APIResponse)
async def create_user(user: KoreanUserAPI):
    """새 사용자 생성"""
    # 실제로는 데이터베이스에 저장
    response = user.to_api_response("사용자가 성공적으로 생성되었습니다")
    return response

@app.get("/users/{user_id}", response_model=APIResponse) 
async def get_user(user_id: str):
    """사용자 조회"""
    # 실제로는 데이터베이스에서 조회
    sample_address = KoreanAddress(
        postal_code="12345",
        city="서울",
        district="강남구",
        street="테헤란로 789"
    )
    
    user = KoreanUserAPI(
        user_id=user_id,
        name="김사용자",
        email="user@example.com", 
        phone="010-1234-5678",
        address=sample_address,
        preferences={"theme": "dark", "language": "ko"}
    )
    
    return user.to_api_response("사용자 조회 성공")

# 배치 데이터 처리용 모델
class KoreanUserBatch(BaseModel):
    """배치 처리용 사용자 모델"""
    users: List[KoreanUserAPI] = Field(..., min_length=1, max_length=100)
    
    def validate_all(self) -> Dict[str, List[str]]:
        """모든 사용자 검증 결과"""
        results = {"valid": [], "invalid": []}
        
        for user in self.users:
            try:
                # 추가 비즈니스 로직 검증
                if user.name and user.email and user.phone:
                    results["valid"].append(user.user_id)
                else:
                    results["invalid"].append(f"{user.user_id}: 필수 정보 누락")
            except Exception as e:
                results["invalid"].append(f"{user.user_id}: {str(e)}")
        
        return results
    
    def to_csv_headers(self) -> List[str]:
        """CSV 헤더 생성"""
        return ["user_id", "name", "email", "phone", "city", "district"]
    
    def to_csv_rows(self) -> List[List[str]]:
        """CSV 행 데이터 생성"""
        rows = []
        for user in self.users:
            rows.append([
                user.user_id,
                user.name,
                user.email,
                user.phone,
                user.address.city,
                user.address.district
            ])
        return rows

# JSON/API 통합 시연
def demonstrate_json_api_integration():
    """JSON/API 통합 시연"""
    print("\nJSON/API 통합:")
    
    # JSON 직렬화/역직렬화
    address = KoreanAddress(
        postal_code="54321",
        city="부산",
        district="해운대구",
        street="해운대해변로 100"
    )
    
    user = KoreanUserAPI(
        user_id="USER123456",
        name="이부산",
        email="busan@example.com",
        phone="010-2222-3333",
        address=address,
        preferences={"newsletter": True, "sms": False}
    )
    
    # JSON 문자열로 변환
    json_str = user.to_json()
    print("[O] JSON 직렬화:")
    print(json_str[:200] + "...")
    
    # JSON에서 객체 복원
    restored_user = KoreanUserAPI.from_json(json_str)
    print(f"[O] JSON 역직렬화: {restored_user.name} ({restored_user.address.city})")
    
    # API 응답 형식
    api_response = user.to_api_response("사용자 정보 조회 성공")
    print(f"[O] API 응답: {api_response.success}, {api_response.message}")
    
    # OpenAPI 스키마 정보
    schema = KoreanUserAPI.model_json_schema()
    print(f"[O] OpenAPI 스키마 생성됨: {len(schema['properties'])}개 필드")
    
    # 배치 처리
    users_data = [user, user]  # 예시로 같은 사용자 2명
    batch = KoreanUserBatch(users=users_data)
    validation_results = batch.validate_all()
    print(f"[O] 배치 검증: 유효 {len(validation_results['valid'])}명, "
          f"무효 {len(validation_results['invalid'])}명")

demonstrate_json_api_integration()
