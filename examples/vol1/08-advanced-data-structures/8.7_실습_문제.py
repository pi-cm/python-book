"""1권 Chapter 8: 고급 데이터 구조 — 8.7 실습 문제

원고: manuscript/chapters/08-advanced-data-structures.md (1836줄부터)
"""

# ---- 원고 1836줄 ----
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

# 1번: dataclass 기본 활용
@dataclass
class Book:
    title: str
    author: str
    pages: int
    price: int = 0
    isbn: Optional[str] = None
    
# 문제: 책 정보를 생성하고 할인 가격을 계산하는 메서드를 추가하세요
# 답:
@dataclass
class Book:
    title: str
    author: str  
    pages: int
    price: int = 0
    isbn: Optional[str] = None
    
    def discounted_price(self, discount_rate: float) -> int:
        return int(self.price * (1 - discount_rate))

book = Book("파이썬 완전정복", "김개발", 500, 35000)
print(f"할인가: {book.discounted_price(0.2):,}원")

# 2번: Enum 활용
class WeekDay(Enum):
    MONDAY = "월요일"
    TUESDAY = "화요일"
    WEDNESDAY = "수요일"
    THURSDAY = "목요일"
    FRIDAY = "금요일"

# 문제: 주말 여부를 확인하는 메서드를 추가하세요
# 답:
class WeekDay(Enum):
    MONDAY = "월요일"
    TUESDAY = "화요일"
    WEDNESDAY = "수요일" 
    THURSDAY = "목요일"
    FRIDAY = "금요일"
    SATURDAY = "토요일"
    SUNDAY = "일요일"
    
    def is_weekend(self) -> bool:
        return self in (WeekDay.SATURDAY, WeekDay.SUNDAY)

print(f"금요일은 주말인가? {WeekDay.FRIDAY.is_weekend()}")

# 3번: NamedTuple 활용
from typing import NamedTuple

class Point(NamedTuple):
    x: float
    y: float

# 문제: 두 점 사이의 거리를 계산하는 메서드를 추가하세요
# 답:
class Point(NamedTuple):
    x: float
    y: float
    
    def distance_to(self, other: 'Point') -> float:
        return ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5

p1 = Point(0, 0)
p2 = Point(3, 4)
print(f"거리: {p1.distance_to(p2)}")

# 4번: defaultdict 활용
from collections import defaultdict

student_scores = [
    ("김철수", "국어", 85),
    ("김철수", "영어", 92),
    ("이영희", "국어", 95),
    ("이영희", "수학", 87)
]

# 문제: 학생별 과목별 점수를 defaultdict로 구성하세요
# 답:
grades = defaultdict(dict)
for name, subject, score in student_scores:
    grades[name][subject] = score

print(f"김철수 성적: {dict(grades['김철수'])}")

# 5번: Counter 활용
from collections import Counter

text = "파이썬은 정말 좋은 언어입니다 파이썬을 배워봅시다"
# 문제: 가장 자주 나타나는 단어 3개를 찾으세요
# 답:
words = text.split()
word_counter = Counter(words)
most_common = word_counter.most_common(3)
print(f"빈출 단어: {most_common}")

# ---- 원고 1944줄 ----
# 6번: 복합 dataclass
@dataclass
class Address:
    city: str
    district: str
    street: str

@dataclass  
class Person:
    name: str
    age: int
    address: Address
    hobbies: List[str] = field(default_factory=list)

# 문제: 같은 지역에 사는지 확인하는 메서드를 추가하세요
# 답:
@dataclass
class Person:
    name: str
    age: int
    address: Address
    hobbies: List[str] = field(default_factory=list)
    
    def lives_in_same_city(self, other: 'Person') -> bool:
        return self.address.city == other.address.city

addr1 = Address("서울", "강남구", "테헤란로")
addr2 = Address("서울", "서초구", "강남대로")
person1 = Person("김철수", 25, addr1)
person2 = Person("이영희", 23, addr2)
print(f"같은 도시: {person1.lives_in_same_city(person2)}")

# 7번: 상태 기계 Enum
class LightState(Enum):
    RED = "빨간불"
    YELLOW = "노란불"  
    GREEN = "초록불"
    
    def next_state(self) -> 'LightState':
        transitions = {
            LightState.RED: LightState.GREEN,
            LightState.GREEN: LightState.YELLOW,
            LightState.YELLOW: LightState.RED
        }
        return transitions[self]

# 문제: 신호등 시뮬레이션을 구현하세요
# 답:
@dataclass
class TrafficLight:
    current_state: LightState = LightState.RED
    
    def change_light(self):
        self.current_state = self.current_state.next_state()
        print(f"신호등: {self.current_state.value}")

light = TrafficLight()
for _ in range(5):
    light.change_light()

# 8번: deque를 활용한 히스토리 관리
from collections import deque

class CommandHistory:
    def __init__(self, max_history: int = 10):
        self.history = deque(maxlen=max_history)
        self.current_index = -1
    
# 문제: 실행 취소/다시 실행 기능을 구현하세요
# 답:
class CommandHistory:
    def __init__(self, max_history: int = 10):
        self.history = deque(maxlen=max_history)
        self.current_index = -1
    
    def execute(self, command: str):
        # 현재 위치 이후의 히스토리 제거
        while len(self.history) > self.current_index + 1:
            self.history.pop()
        
        self.history.append(command)
        self.current_index += 1
        print(f"실행: {command}")
    
    def undo(self) -> Optional[str]:
        if self.current_index >= 0:
            command = self.history[self.current_index]
            self.current_index -= 1
            print(f"실행 취소: {command}")
            return command
        return None
    
    def redo(self) -> Optional[str]:
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            command = self.history[self.current_index]
            print(f"다시 실행: {command}")
            return command
        return None

history = CommandHistory()
history.execute("파일 열기")
history.execute("텍스트 입력")
history.undo()
history.redo()

# 9번: Generic dataclass
from typing import TypeVar, Generic

T = TypeVar('T')

@dataclass
class Stack(Generic[T]):
    items: List[T] = field(default_factory=list)
    
# 문제: push, pop, peek 메서드를 구현하세요
# 답:
@dataclass
class Stack(Generic[T]):
    items: List[T] = field(default_factory=list)
    
    def push(self, item: T):
        self.items.append(item)
    
    def pop(self) -> Optional[T]:
        return self.items.pop() if self.items else None
    
    def peek(self) -> Optional[T]:
        return self.items[-1] if self.items else None
    
    def is_empty(self) -> bool:
        return len(self.items) == 0

int_stack = Stack[int]()
int_stack.push(1)
int_stack.push(2)
print(f"peek: {int_stack.peek()}")
print(f"pop: {int_stack.pop()}")

# 10번: ChainMap 설정 관리
from collections import ChainMap

# 문제: 환경별 설정을 ChainMap으로 관리하는 클래스를 만드세요
# 답:
class ConfigManager:
    def __init__(self):
        self.default_config = {
            "timeout": 30,
            "retry_count": 3,
            "log_level": "INFO"
        }
        self.user_config = {}
        self.runtime_config = {}
        self.config = ChainMap(
            self.runtime_config,
            self.user_config, 
            self.default_config
        )
    
    def set_user_config(self, **kwargs):
        self.user_config.update(kwargs)
    
    def set_runtime_config(self, **kwargs):
        self.runtime_config.update(kwargs)
    
    def get(self, key: str, default=None):
        return self.config.get(key, default)
    
    def get_all_configs(self) -> Dict[str, Any]:
        return dict(self.config)

config_mgr = ConfigManager()
config_mgr.set_user_config(timeout=60, log_level="DEBUG")
config_mgr.set_runtime_config(retry_count=5)

print(f"최종 설정: {config_mgr.get_all_configs()}")

# ---- 원고 2127줄 ----
# 11번: 복잡한 dataclass 상속
@dataclass
class Vehicle:
    brand: str
    model: str
    year: int
    
    def get_age(self) -> int:
        return datetime.now().year - self.year

@dataclass
class Car(Vehicle):
    doors: int = 4
    fuel_type: str = "gasoline"

@dataclass  
class ElectricCar(Car):
    battery_capacity: float = 0.0
    range_km: int = 0
    fuel_type: str = field(default="electric", init=False)

# 문제: 전기차의 효율성을 계산하는 메서드를 추가하세요
# 답:
@dataclass
class ElectricCar(Car):
    battery_capacity: float = 0.0
    range_km: int = 0
    fuel_type: str = field(default="electric", init=False)
    
    def efficiency_km_per_kwh(self) -> float:
        if self.battery_capacity <= 0:
            return 0.0
        return self.range_km / self.battery_capacity
    
    def charging_cost(self, electricity_price_per_kwh: float) -> float:
        return self.battery_capacity * electricity_price_per_kwh

tesla = ElectricCar("Tesla", "Model 3", 2023, battery_capacity=75.0, range_km=500)
print(f"효율성: {tesla.efficiency_km_per_kwh():.2f} km/kWh")
print(f"충전 비용: {tesla.charging_cost(300):.0f}원")

# 12번: 고급 Enum with 메서드
class HTTPStatus(Enum):
    OK = 200
    NOT_FOUND = 404
    INTERNAL_ERROR = 500
    
    def is_success(self) -> bool:
        return 200 <= self.value < 300
    
    def is_client_error(self) -> bool:
        return 400 <= self.value < 500
    
    def is_server_error(self) -> bool:
        return 500 <= self.value < 600

# 문제: HTTP 응답을 관리하는 클래스를 만드세요
# 답:
@dataclass
class HTTPResponse:
    status: HTTPStatus
    body: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    
    def is_successful(self) -> bool:
        return self.status.is_success()
    
    def add_header(self, key: str, value: str):
        self.headers[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status_code": self.status.value,
            "status_name": self.status.name,
            "body": self.body,
            "headers": self.headers,
            "is_successful": self.is_successful()
        }

response = HTTPResponse(HTTPStatus.OK, "Success", {"Content-Type": "application/json"})
print(f"응답 정보: {response.to_dict()}")

# 13번: 복잡한 데이터 구조 관리
@dataclass
class Task:
    id: str
    title: str
    priority: int
    completed: bool = False
    dependencies: Set[str] = field(default_factory=set)
    
class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.completion_order: deque = deque(maxlen=50)
    
# 문제: 의존성을 고려한 작업 완료 시스템을 구현하세요
# 답:
class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.completion_order: deque = deque(maxlen=50)
    
    def add_task(self, task: Task):
        self.tasks[task.id] = task
    
    def can_complete_task(self, task_id: str) -> bool:
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if task.completed:
            return False
        
        # 모든 의존성 작업이 완료되었는지 확인
        for dep_id in task.dependencies:
            if dep_id in self.tasks and not self.tasks[dep_id].completed:
                return False
        
        return True
    
    def complete_task(self, task_id: str) -> bool:
        if not self.can_complete_task(task_id):
            return False
        
        self.tasks[task_id].completed = True
        self.completion_order.append(task_id)
        print(f"[O] 작업 완료: {self.tasks[task_id].title}")
        return True
    
    def get_available_tasks(self) -> List[Task]:
        return [task for task in self.tasks.values() 
                if self.can_complete_task(task.id)]

# 테스트
manager = TaskManager()
manager.add_task(Task("1", "기초 설계", 3))
manager.add_task(Task("2", "상세 설계", 2, dependencies={"1"}))
manager.add_task(Task("3", "개발", 1, dependencies={"2"}))
manager.add_task(Task("4", "테스트", 1, dependencies={"3"}))

manager.complete_task("1")
manager.complete_task("2")
available = manager.get_available_tasks()
print(f"수행 가능한 작업: {[t.title for t in available]}")

# 14번: 멀티레벨 캐시 시스템
from collections import OrderedDict

class MultiLevelCache:
    def __init__(self, l1_size: int = 10, l2_size: int = 50):
        self.l1_cache: OrderedDict = OrderedDict()  # LRU 캐시
        self.l2_cache: Dict[str, Any] = {}  # 단순 딕셔너리
        self.l1_size = l1_size
        self.l2_size = l2_size
        self.stats = defaultdict(int)
    
# 문제: 계층적 캐시 시스템의 get/put을 구현하세요
# 답:
class MultiLevelCache:
    def __init__(self, l1_size: int = 10, l2_size: int = 50):
        self.l1_cache: OrderedDict = OrderedDict()
        self.l2_cache: Dict[str, Any] = {}
        self.l1_size = l1_size
        self.l2_size = l2_size
        self.stats = defaultdict(int)
    
    def get(self, key: str) -> Optional[Any]:
        # L1 캐시 확인
        if key in self.l1_cache:
            # LRU 업데이트
            value = self.l1_cache.pop(key)
            self.l1_cache[key] = value
            self.stats["l1_hits"] += 1
            return value
        
        # L2 캐시 확인
        if key in self.l2_cache:
            value = self.l2_cache[key]
            # L1으로 승격
            self._put_l1(key, value)
            self.stats["l2_hits"] += 1
            return value
        
        self.stats["misses"] += 1
        return None
    
    def put(self, key: str, value: Any):
        # L1에 저장
        self._put_l1(key, value)
        # L2에도 저장
        self._put_l2(key, value)
    
    def _put_l1(self, key: str, value: Any):
        if key in self.l1_cache:
            self.l1_cache.pop(key)
        elif len(self.l1_cache) >= self.l1_size:
            # LRU 제거
            evicted_key, evicted_value = self.l1_cache.popitem(last=False)
            # L2로 이동
            self._put_l2(evicted_key, evicted_value)
        
        self.l1_cache[key] = value
    
    def _put_l2(self, key: str, value: Any):
        if len(self.l2_cache) >= self.l2_size and key not in self.l2_cache:
            # 임의의 항목 제거 (단순화)
            oldest_key = next(iter(self.l2_cache))
            del self.l2_cache[oldest_key]
        
        self.l2_cache[key] = value
    
    def get_stats(self) -> Dict[str, Any]:
        total_requests = sum(self.stats.values())
        if total_requests == 0:
            return self.stats
        
        return {
            **dict(self.stats),
            "hit_rate": (self.stats["l1_hits"] + self.stats["l2_hits"]) / total_requests,
            "l1_hit_rate": self.stats["l1_hits"] / total_requests,
            "l2_hit_rate": self.stats["l2_hits"] / total_requests
        }

# 캐시 테스트
cache = MultiLevelCache(l1_size=3, l2_size=5)
for i in range(10):
    cache.put(f"key_{i}", f"value_{i}")

# 액세스 패턴 시뮬레이션
for key in ["key_1", "key_2", "key_1", "key_5", "key_9", "key_1"]:
    value = cache.get(key)
    print(f"GET {key}: {value}")

print(f"캐시 통계: {cache.get_stats()}")

# 15번: 고급 타입 힌팅과 데이터 검증
from typing import Protocol, runtime_checkable
from dataclasses import dataclass, field, asdict
import json

@runtime_checkable
class Serializable(Protocol):
    def to_dict(self) -> Dict[str, Any]:
        ...
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Serializable':
        ...

@dataclass
class Address:
    street: str
    city: str
    postal_code: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Address':
        return cls(**data)

@dataclass
class Person:
    name: str
    age: int
    address: Address
    emails: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.age < 0:
            raise ValueError("나이는 0 이상이어야 합니다")
        if not self.name.strip():
            raise ValueError("이름은 비어있을 수 없습니다")
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Person':
        address_data = data.pop('address')
        address = Address.from_dict(address_data)
        return cls(address=address, **data)

# 문제: JSON 직렬화/역직렬화 관리자를 만드세요
# 답:
class SerializationManager:
    @staticmethod
    def to_json(obj: Serializable) -> str:
        if not isinstance(obj, Serializable):
            raise TypeError(f"{type(obj)}는 Serializable 프로토콜을 구현해야 합니다")
        return json.dumps(obj.to_dict(), ensure_ascii=False, indent=2)
    
    @staticmethod
    def from_json(json_str: str, cls: type) -> Serializable:
        if not hasattr(cls, 'from_dict'):
            raise TypeError(f"{cls}는 from_dict 메서드가 필요합니다")
        data = json.loads(json_str)
        return cls.from_dict(data)

# 테스트
address = Address("테헤란로 123", "서울", "06234")
person = Person("김철수", 30, address, ["kim@example.com"])

# 직렬화
json_str = SerializationManager.to_json(person)
print("JSON 직렬화:")
print(json_str)

# 역직렬화
restored_person = SerializationManager.from_json(json_str, Person)
print(f"\n복원된 객체: {restored_person.name}, {restored_person.address.city}")
