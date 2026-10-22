"""1권 Chapter 11: 객체 지향 프로그래밍 — 11.2 속성과 메서드 고급 활용

원고: manuscript/chapters/11-object-oriented-programming.md (207줄부터)
"""

# ---- 원고 207줄 ----
from datetime import datetime, date
from typing import Optional
import re

class KoreanPerson:
    """한국인 정보 클래스 (프로퍼티 활용)"""
    
    def __init__(self, name: str, birth_date: str, phone: str = None):
        self._name = name
        self._birth_date = self._validate_date(birth_date)
        self._phone = phone
        self._email = None
    
    @property
    def name(self) -> str:
        """이름 프로퍼티 (읽기 전용)"""
        return self._name
    
    @property
    def age(self) -> int:
        """나이 자동 계산 프로퍼티"""
        today = date.today()
        birth = datetime.strptime(self._birth_date, "%Y-%m-%d").date()
        age = today.year - birth.year
        
        # 생일이 지나지 않았으면 1살 빼기
        if today < birth.replace(year=today.year):
            age -= 1
        
        return age
    
    @property
    def korean_age(self) -> int:
        """세는 나이 계산 (올해 연도 - 출생연도 + 1)"""
        return date.today().year - self.birth_year + 1
    
    @property
    def birth_year(self) -> int:
        """출생연도"""
        return datetime.strptime(self._birth_date, "%Y-%m-%d").year
    
    @property
    def phone(self) -> Optional[str]:
        """전화번호"""
        return self._phone
    
    @phone.setter
    def phone(self, value: str) -> None:
        """전화번호 설정 (유효성 검사 포함)"""
        if value is None:
            self._phone = None
            return
        
        # 한국 휴대폰 번호 형식 검증
        phone_pattern = r'^010-\d{4}-\d{4}$'
        if not re.match(phone_pattern, value):
            raise ValueError("올바른 휴대폰 번호 형식이 아닙니다 (010-0000-0000)")
        
        self._phone = value
    
    @property
    def email(self) -> Optional[str]:
        """이메일"""
        return self._email
    
    @email.setter
    def email(self, value: str) -> None:
        """이메일 설정 (유효성 검사 포함)"""
        if value is None:
            self._email = None
            return
        
        # 간단한 이메일 형식 검증
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise ValueError("올바른 이메일 형식이 아닙니다")
        
        self._email = value
    
    @staticmethod
    def _validate_date(date_str: str) -> str:
        """날짜 형식 검증"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            raise ValueError("날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)")
    
    def introduce(self) -> str:
        """자기소개"""
        intro = f"안녕하세요! {self.name}입니다."
        intro += f" {self.age}세 ({self.korean_age}세, 한국나이)이고"
        intro += f" {self.birth_year}년생입니다."
        
        if self.phone:
            intro += f" 연락처는 {self.phone}입니다."
        
        return intro

# 사용 예제
person = KoreanPerson("김철수", "1995-05-15")
print(person.introduce())

# 프로퍼티 활용
print(f"만 나이: {person.age}세")
print(f"한국 나이: {person.korean_age}세")

# setter를 통한 값 설정
person.phone = "010-1234-5678"
person.email = "kim@example.com"

print(f"전화번호: {person.phone}")
print(f"이메일: {person.email}")

# 잘못된 형식 입력 시 에러 발생
try:
    person.phone = "010-12345-6789"  # 잘못된 형식
except ValueError as e:
    print(f"오류: {e}")

# ---- 원고 347줄 ----
from typing import ClassVar, List
from datetime import datetime
import json

class KoreanUniversity:
    """한국 대학교 클래스"""
    
    # 클래스 변수 (타입 힌트 포함)
    total_universities: ClassVar[int] = 0
    university_list: ClassVar[List[str]] = []
    
    def __init__(self, name: str, location: str, founded_year: int):
        self.name = name
        self.location = location
        self.founded_year = founded_year
        self.student_count = 0
        self.departments: List[str] = []
        
        # 클래스 변수 업데이트
        KoreanUniversity.total_universities += 1
        KoreanUniversity.university_list.append(name)
    
    @classmethod
    def create_from_dict(cls, data: dict) -> 'KoreanUniversity':
        """딕셔너리로부터 대학교 객체 생성"""
        return cls(
            name=data['name'],
            location=data['location'],
            founded_year=data['founded_year']
        )
    
    @classmethod
    def create_from_json(cls, json_str: str) -> 'KoreanUniversity':
        """JSON 문자열로부터 대학교 객체 생성"""
        data = json.loads(json_str)
        return cls.create_from_dict(data)
    
    @classmethod
    def get_statistics(cls) -> dict:
        """대학교 통계 반환"""
        return {
            "총_대학수": cls.total_universities,
            "대학_목록": cls.university_list.copy(),
            "등록_시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @staticmethod
    def is_valid_year(year: int) -> bool:
        """설립 연도 유효성 검사 (정적 메서드)"""
        current_year = datetime.now().year
        return 1000 <= year <= current_year  # 천 년보다 이전 연도는 잘못 입력한 값으로 본다
    
    @staticmethod
    def calculate_history_length(founded_year: int) -> int:
        """대학 역사 계산"""
        return datetime.now().year - founded_year
    
    def add_department(self, department: str) -> None:
        """학과 추가"""
        if department not in self.departments:
            self.departments.append(department)
            print(f"[O] {self.name}에 {department} 추가됨")
        else:
            print(f"[X] {department}는 이미 존재합니다")
    
    def get_info(self) -> dict:
        """대학교 정보 반환"""
        return {
            "대학명": self.name,
            "소재지": self.location,
            "설립년도": self.founded_year,
            "역사": f"{self.calculate_history_length(self.founded_year)}년",
            "학생수": f"{self.student_count:,}명",
            "학과수": len(self.departments),
            "학과목록": self.departments
        }

# 사용 예제
# 일반적인 생성
snu = KoreanUniversity("서울대학교", "서울", 1946)
yonsei = KoreanUniversity("연세대학교", "서울", 1885)

# 클래스 메서드를 통한 생성
korea_data = {
    "name": "고려대학교",
    "location": "서울", 
    "founded_year": 1905
}
korea_univ = KoreanUniversity.create_from_dict(korea_data)

# JSON을 통한 생성
kaist_json = '{"name": "KAIST", "location": "대전", "founded_year": 1971}'
kaist = KoreanUniversity.create_from_json(kaist_json)

# 학과 추가
snu.add_department("컴퓨터공학과")
snu.add_department("경영학과")
snu.student_count = 28000

# 정적 메서드 사용
print(f"1885년이 유효한 설립연도인가? {KoreanUniversity.is_valid_year(1885)}")
print(f"연세대 역사: {KoreanUniversity.calculate_history_length(1885)}년")

# 클래스 메서드로 통계 확인
stats = KoreanUniversity.get_statistics()
print(f"\n대학교 통계:")
for key, value in stats.items():
    print(f"{key}: {value}")

# 개별 대학 정보
print(f"\n서울대 정보:")
for key, value in snu.get_info().items():
    print(f"{key}: {value}")
