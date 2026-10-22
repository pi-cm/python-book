"""1권 Chapter 2. 변수와 데이터 — 2.3 타입 힌트 (Type Hints) 완전 가이드

원고: manuscript/chapters/02-variables-data.md (508줄부터)
"""

# ---- 원고 508줄 ----
from typing import List, Dict, Tuple, Set, Optional, Union, Any

# 기본 타입들
def 기본_타입_예제(
    이름: str,
    나이: int,
    키: float,
    결혼여부: bool
) -> str:
    return f"{이름}({나이}세, {키}cm, {'기혼' if 결혼여부 else '미혼'})"

# 컬렉션 타입들
학생_성적: List[int] = [90, 85, 92, 88]
사용자_정보: Dict[str, Any] = {"이름": "김학생", "나이": 20}
좌표: Tuple[float, float] = (37.5665, 126.9780)
고유_번호들: Set[int] = {1, 2, 3, 4, 5}

# ---- 원고 531줄 ----
from typing import Callable, TypeVar, Generic, Protocol, Literal, List, Optional, Union
from typing import TypedDict  # Python 3.8+

# Optional과 Union
def 선택적_매개변수(이름: str, 나이: Optional[int] = None) -> str:
    if 나이 is None:
        return f"이름: {이름}"
    return f"이름: {이름}, 나이: {나이}"

def 여러_타입_허용(값: Union[str, int, float]) -> str:
    return f"받은 값: {값} (타입: {type(값).__name__})"

# Literal 타입 (Python 3.8+)
def 상태_확인(상태: Literal["대기", "진행", "완료"]) -> bool:
    return 상태 == "완료"

# Callable 타입
def 함수_실행기(함수: Callable[[int, int], int], a: int, b: int) -> int:
    return 함수(a, b)

더하기: Callable[[int, int], int] = lambda x, y: x + y
결과 = 함수_실행기(더하기, 10, 20)

# TypedDict (구조화된 딕셔너리)
class 학생정보(TypedDict):
    이름: str
    나이: int
    성적: List[int]

학생: 학생정보 = {
    "이름": "홍길동",
    "나이": 18,
    "성적": [90, 85, 92]
}

# ---- 원고 572줄 ----
from typing import TypeVar, Generic, List

# 타입 변수 정의
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

# 제네릭 클래스
class 스택(Generic[T]):
    def __init__(self) -> None:
        self._items: List[T] = []
    
    def push(self, item: T) -> None:
        self._items.append(item)
    
    def pop(self) -> T:
        if not self._items:
            raise IndexError("빈 스택입니다")
        return self._items.pop()
    
    def is_empty(self) -> bool:
        return len(self._items) == 0

# 제네릭 함수
def 첫_번째_요소(리스트: List[T]) -> T:
    if not 리스트:
        raise ValueError("빈 리스트입니다")
    return 리스트[0]

# 사용 예제
숫자_스택 = 스택[int]()
숫자_스택.push(1)
숫자_스택.push(2)

문자_스택 = 스택[str]()
문자_스택.push("안녕")
문자_스택.push("파이썬")

숫자들 = [1, 2, 3, 4, 5]
첫_숫자 = 첫_번째_요소(숫자들)  # 타입: int

# ---- 원고 619줄 ----
from typing import List, Protocol

# Protocol 정의
class 크기측정가능(Protocol):
    def __len__(self) -> int: ...

class 정렬가능(Protocol):
    def __lt__(self, other) -> bool: ...

# Protocol을 사용하는 함수
def 길이_출력(객체: 크기측정가능) -> None:
    print(f"길이: {len(객체)}")

def 정렬_함수(항목들: List[정렬가능]) -> List[정렬가능]:
    return sorted(항목들)

# 사용 - 명시적 상속 없이도 동작
길이_출력("문자열")      # str은 __len__ 구현
길이_출력([1, 2, 3])   # list도 __len__ 구현
길이_출력({1, 2})      # set도 __len__ 구현

숫자들 = [3, 1, 4, 1, 5]
정렬된_숫자 = 정렬_함수(숫자들)  # int는 __lt__ 구현
