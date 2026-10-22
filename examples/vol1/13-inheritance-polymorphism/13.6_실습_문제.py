"""1권 Chapter 13: 상속과 다형성 (Inheritance and Polymorphism) — 13.6 실습 문제

원고: manuscript/chapters/13-inheritance-polymorphism.md (2627줄부터)
"""

# ---- 원고 2627줄 ----
# 1번: 기본 상속 구현
class Vehicle:
    def __init__(self, brand: str, model: str):
        self.brand = brand
        self.model = model
        self.speed = 0
    
    def accelerate(self, increment: int) -> None:
        # 문제: 속도 증가 메서드 구현
        pass
    
    def brake(self, decrement: int) -> None:
        # 문제: 속도 감소 메서드 구현 (0 이하로 내려가지 않게)
        pass

class Car(Vehicle):
    def __init__(self, brand: str, model: str, doors: int):
        # 문제: 부모 클래스 초기화 호출
        pass
        self.doors = doors
    
    def honk(self) -> str:
        # 문제: 클랙션 메서드 구현
        pass

# 답안:
class Vehicle:
    def __init__(self, brand: str, model: str):
        self.brand = brand
        self.model = model
        self.speed = 0
    
    def accelerate(self, increment: int) -> None:
        self.speed += increment
        print(f"속도 증가: {self.speed}km/h")
    
    def brake(self, decrement: int) -> None:
        self.speed = max(0, self.speed - decrement)
        print(f"속도 감소: {self.speed}km/h")

class Car(Vehicle):
    def __init__(self, brand: str, model: str, doors: int):
        super().__init__(brand, model)
        self.doors = doors
    
    def honk(self) -> str:
        return f"{self.brand} {self.model}: 빵빵!"

# 테스트
car = Car("현대", "소나타", 4)
car.accelerate(60)
car.brake(20)
print(car.honk())

# 2번: 메서드 오버라이딩
class Animal:
    def __init__(self, name: str):
        self.name = name
    
    def make_sound(self) -> str:
        return "동물이 소리를 냅니다"
    
    def move(self) -> str:
        return f"{self.name}: 이동합니다"

class Dog(Animal):
    # 문제: make_sound 메서드를 오버라이드하여 "멍멍!"을 반환
    pass

class Fish(Animal):
    # 문제: move 메서드를 오버라이드하여 "수영"을 포함한 문자열 반환
    pass

# 답안:
class Dog(Animal):
    def make_sound(self) -> str:
        return f"{self.name}: 멍멍!"

class Fish(Animal):
    def move(self) -> str:
        return f"{self.name}: 물속에서 수영합니다"

# 테스트
dog = Dog("바둑이")
fish = Fish("금붕어")
print(dog.make_sound())
print(dog.move())
print(fish.move())

# 3번: super() 활용
class Employee:
    def __init__(self, name: str, salary: int):
        self.name = name
        self.salary = salary
    
    def get_annual_bonus(self) -> int:
        return self.salary // 12  # 월급의 1개월분

class Manager(Employee):
    def __init__(self, name: str, salary: int, team_size: int):
        # 문제: super()를 사용하여 부모 클래스 초기화
        pass
        self.team_size = team_size
    
    def get_annual_bonus(self) -> int:
        # 문제: 부모의 보너스 + 팀원 수 * 50000 추가
        pass

# 답안:
class Manager(Employee):
    def __init__(self, name: str, salary: int, team_size: int):
        super().__init__(name, salary)
        self.team_size = team_size
    
    def get_annual_bonus(self) -> int:
        base_bonus = super().get_annual_bonus()
        return base_bonus + (self.team_size * 50000)

# 테스트
manager = Manager("김팀장", 5000000, 5)
print(f"연간 보너스: {manager.get_annual_bonus():,}원")

# 4번: 추상 클래스 구현
from abc import ABC, abstractmethod

class Shape(ABC):
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def calculate_area(self) -> float:
        pass
    
    @abstractmethod
    def calculate_perimeter(self) -> float:
        pass
    
    def describe(self) -> str:
        return f"{self.name}: 넓이 {self.calculate_area():.2f}, 둘레 {self.calculate_perimeter():.2f}"

# 문제: Rectangle 클래스 구현
class Rectangle(Shape):
    pass

# 문제: Circle 클래스 구현
class Circle(Shape):
    pass

# 답안:
import math

class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        super().__init__("직사각형")
        self.width = width
        self.height = height
    
    def calculate_area(self) -> float:
        return self.width * self.height
    
    def calculate_perimeter(self) -> float:
        return 2 * (self.width + self.height)

class Circle(Shape):
    def __init__(self, radius: float):
        super().__init__("원")
        self.radius = radius
    
    def calculate_area(self) -> float:
        return math.pi * self.radius ** 2
    
    def calculate_perimeter(self) -> float:
        return 2 * math.pi * self.radius

# 테스트
shapes = [
    Rectangle(5, 3),
    Circle(4)
]

for shape in shapes:
    print(shape.describe())

# 5번: 다중 상속과 MRO
class Flyable:
    def fly(self) -> str:
        return "날고 있습니다"

class Swimmable:
    def swim(self) -> str:
        return "수영하고 있습니다"

class Bird:
    def __init__(self, name: str):
        self.name = name
    
    def chirp(self) -> str:
        return f"{self.name}: 짹짹!"

# 문제: Duck 클래스가 Bird, Flyable, Swimmable을 모두 상속받도록 구현
class Duck(Bird, Flyable, Swimmable):
    def __init__(self, name: str):
        # 문제: super()를 올바르게 사용
        pass
    
    def quack(self) -> str:
        # 문제: 오리 특유의 소리 구현
        pass

# 답안:
class Duck(Bird, Flyable, Swimmable):
    def __init__(self, name: str):
        super().__init__(name)
    
    def quack(self) -> str:
        return f"{self.name}: 꽥꽥!"
    
    def show_abilities(self) -> None:
        print(self.chirp())
        print(self.quack()) 
        print(self.fly())
        print(self.swim())

# MRO 확인
print("Duck MRO:", [cls.__name__ for cls in Duck.__mro__])

# 테스트
duck = Duck("도널드")
duck.show_abilities()

# ---- 원고 2863줄 ----
# 6번: 프로퍼티와 상속
class BankAccount:
    def __init__(self, owner: str, balance: int = 0):
        self.owner = owner
        self._balance = balance
        self._transaction_fee = 1000
    
    @property
    def balance(self) -> int:
        return self._balance
    
    def withdraw(self, amount: int) -> bool:
        if amount + self._transaction_fee <= self._balance:
            self._balance -= (amount + self._transaction_fee)
            return True
        return False

class PremiumAccount(BankAccount):
    def __init__(self, owner: str, balance: int = 0):
        super().__init__(owner, balance)
        self._transaction_fee = 0  # 프리미엄은 수수료 무료
        self._monthly_limit = 10000000
    
    # 문제: withdraw 메서드를 오버라이드하여 월 한도 체크 추가
    def withdraw(self, amount: int) -> bool:
        # 월 한도 체크 로직 추가 필요
        pass

# 답안:
class PremiumAccount(BankAccount):
    def __init__(self, owner: str, balance: int = 0):
        super().__init__(owner, balance)
        self._transaction_fee = 0
        self._monthly_limit = 10000000
        self._monthly_withdrawn = 0
    
    def withdraw(self, amount: int) -> bool:
        if self._monthly_withdrawn + amount > self._monthly_limit:
            print(f"월 한도 초과: {self._monthly_limit:,}원")
            return False
        
        success = super().withdraw(amount)
        if success:
            self._monthly_withdrawn += amount
        return success
    
    def reset_monthly_limit(self):
        """월 한도 리셋"""
        self._monthly_withdrawn = 0

# 7번: 팩토리 패턴과 상속
from abc import ABC, abstractmethod

class Vehicle(ABC):
    @abstractmethod
    def start(self) -> str:
        pass
    
    @abstractmethod
    def stop(self) -> str:
        pass

class Car(Vehicle):
    def start(self) -> str:
        return "자동차 시동 켜짐"
    
    def stop(self) -> str:
        return "자동차 시동 꺼짐"

class Motorcycle(Vehicle):
    def start(self) -> str:
        return "오토바이 시동 켜짐"
    
    def stop(self) -> str:
        return "오토바이 시동 꺼짐"

# 문제: VehicleFactory 클래스 구현
class VehicleFactory:
    @staticmethod
    def create_vehicle(vehicle_type: str) -> Vehicle:
        # 문제: 타입에 따라 적절한 Vehicle 반환
        pass

# 답안:
class VehicleFactory:
    @staticmethod
    def create_vehicle(vehicle_type: str) -> Vehicle:
        if vehicle_type.lower() == "car":
            return Car()
        elif vehicle_type.lower() == "motorcycle":
            return Motorcycle()
        else:
            raise ValueError(f"알 수 없는 차량 타입: {vehicle_type}")

# 테스트
vehicles = [
    VehicleFactory.create_vehicle("car"),
    VehicleFactory.create_vehicle("motorcycle")
]

for vehicle in vehicles:
    print(vehicle.start())
    print(vehicle.stop())

# 8번: 믹스인 패턴
from datetime import datetime

class TimestampMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def touch(self):
        """수정 시간 업데이트"""
        self.updated_at = datetime.now()

class ValidationMixin:
    def validate(self) -> bool:
        """기본 검증"""
        return True

# 문제: User 클래스가 두 믹스인을 사용하도록 구현
class User:
    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email

# 답안:
class User(TimestampMixin, ValidationMixin):
    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email
        super().__init__()  # 믹스인 초기화
    
    def validate(self) -> bool:
        """사용자 정보 검증"""
        if len(self.username) < 3:
            return False
        if "@" not in self.email:
            return False
        return super().validate()
    
    def update_profile(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.touch()  # 수정 시간 업데이트

# 테스트
user = User("김사용자", "user@example.com")
print(f"유효성 검사: {user.validate()}")
print(f"생성 시간: {user.created_at}")

user.update_profile(email="new@example.com")
print(f"수정 시간: {user.updated_at}")

# 9번: 다형성과 덕 타이핑
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> str: ...

class Button:
    def __init__(self, text: str):
        self.text = text
    
    def draw(self) -> str:
        return f"[{self.text}] 버튼"

class Icon:
    def __init__(self, name: str):
        self.name = name
    
    def draw(self) -> str:
        return f"{self.name} 아이콘"

# 문제: render_ui 함수가 Drawable 프로토콜을 활용하도록 구현
def render_ui(components: list[Drawable]) -> None:
    # 문제: 모든 컴포넌트의 draw 메서드 호출
    pass

# 답안:
def render_ui(components: list[Drawable]) -> None:
    print("UI 렌더링 시작:")
    for component in components:
        print(f"  {component.draw()}")
    print("UI 렌더링 완료")

# 테스트
ui_components = [
    Button("확인"),
    Button("취소"),
    Icon("홈"),
    Icon("설정")
]

render_ui(ui_components)

# 10번: 컨텍스트 매니저와 상속
from contextlib import contextmanager

class DatabaseConnection:
    def __init__(self, host: str, db_name: str):
        self.host = host
        self.db_name = db_name
        self.connected = False
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False
    
    def connect(self):
        self.connected = True
        print(f"{self.host}의 {self.db_name}에 연결")
    
    def disconnect(self):
        self.connected = False
        print(f"{self.db_name} 연결 해제")

class PostgreSQLConnection(DatabaseConnection):
    def __init__(self, host: str, db_name: str, port: int = 5432):
        super().__init__(host, db_name)
        self.port = port
    
    # 문제: PostgreSQL 전용 기능 추가
    def execute_query(self, query: str) -> str:
        if not self.connected:
            return "연결되지 않음"
        return f"PostgreSQL에서 쿼리 실행: {query}"

# 답안은 이미 구현됨

# 테스트
with PostgreSQLConnection("localhost", "myapp", 5432) as db:
    result = db.execute_query("SELECT * FROM users")
    print(result)

# ---- 원고 3111줄 ----
# 11번: 메타클래스와 상속
class SingletonMeta(type):
    """싱글톤 메타클래스"""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class DatabaseManager(metaclass=SingletonMeta):
    def __init__(self):
        self.connections = []
    
    def add_connection(self, conn_string: str):
        self.connections.append(conn_string)

# 테스트
db1 = DatabaseManager()
db2 = DatabaseManager()
print(f"동일한 객체인가? {db1 is db2}")

# 12번: 제네릭과 상속
from typing import TypeVar, Generic, List

T = TypeVar('T')

class Repository(Generic[T]):
    """제네릭 저장소"""
    def __init__(self):
        self._items: List[T] = []
    
    def add(self, item: T) -> None:
        self._items.append(item)
    
    def get_all(self) -> List[T]:
        return self._items.copy()
    
    def find_by_id(self, item_id: str) -> T | None:
        # 문제: ID로 항목 찾기 구현 (hasattr 활용)
        pass

# 답안:
class Repository(Generic[T]):
    def __init__(self):
        self._items: List[T] = []
    
    def add(self, item: T) -> None:
        self._items.append(item)
    
    def get_all(self) -> List[T]:
        return self._items.copy()
    
    def find_by_id(self, item_id: str) -> T | None:
        for item in self._items:
            if hasattr(item, 'id') and item.id == item_id:
                return item
        return None

class User:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

# 테스트
user_repo = Repository[User]()
user_repo.add(User("1", "김사용자"))
user_repo.add(User("2", "이사용자"))

found_user = user_repo.find_by_id("1")
print(f"찾은 사용자: {found_user.name if found_user else 'None'}")

# 13번: 비동기와 상속
import asyncio
from abc import ABC, abstractmethod

class AsyncProcessor(ABC):
    @abstractmethod
    async def process(self, data: str) -> str:
        pass

class FileProcessor(AsyncProcessor):
    async def process(self, data: str) -> str:
        # 파일 처리 시뮬레이션
        await asyncio.sleep(0.1)
        return f"파일 처리 완료: {data}"

class NetworkProcessor(AsyncProcessor):
    async def process(self, data: str) -> str:
        # 네트워크 처리 시뮬레이션
        await asyncio.sleep(0.2)
        return f"네트워크 전송 완료: {data}"

# 문제: 다양한 프로세서를 비동기로 실행하는 함수 구현
async def process_all(processors: List[AsyncProcessor], data: str) -> List[str]:
    # 문제: 모든 프로세서를 동시에 실행
    pass

# 답안:
async def process_all(processors: List[AsyncProcessor], data: str) -> List[str]:
    tasks = [processor.process(data) for processor in processors]
    results = await asyncio.gather(*tasks)
    return results

# 테스트
async def main():
    processors = [
        FileProcessor(),
        NetworkProcessor()
    ]
    
    results = await process_all(processors, "테스트 데이터")
    for result in results:
        print(result)

# asyncio.run(main())

# 14번: 데코레이터와 상속
from functools import wraps

def log_method_calls(cls):
    """클래스의 모든 메서드 호출을 로깅하는 데코레이터"""
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and not attr_name.startswith('_'):
            setattr(cls, attr_name, _log_wrapper(attr, attr_name))
    return cls

def _log_wrapper(method, method_name):
    @wraps(method)
    def wrapper(*args, **kwargs):
        print(f"{method_name} 메서드 호출")
        result = method(*args, **kwargs)
        print(f"[O] {method_name} 메서드 완료")
        return result
    return wrapper

@log_method_calls
class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b
    
    def multiply(self, a: int, b: int) -> int:
        return a * b

# 테스트
calc = Calculator()
print(calc.add(5, 3))
print(calc.multiply(4, 7))

# 15번: 종합 프로젝트 - 게임 캐릭터 시스템
from typing import Dict, List
from enum import Enum
import random

class CharacterClass(Enum):
    WARRIOR = "전사"
    MAGE = "마법사" 
    ARCHER = "궁수"
    HEALER = "힐러"

class Skill(ABC):
    def __init__(self, name: str, damage: int, mana_cost: int):
        self.name = name
        self.damage = damage
        self.mana_cost = mana_cost
    
    @abstractmethod
    def use(self, caster: 'Character', target: 'Character') -> str:
        pass

class AttackSkill(Skill):
    def use(self, caster: 'Character', target: 'Character') -> str:
        if caster.mana < self.mana_cost:
            return f"{caster.name}의 마나가 부족합니다!"
        
        caster.mana -= self.mana_cost
        damage = self.damage + random.randint(-5, 5)
        target.take_damage(damage)
        return f"{caster.name}의 {self.name}! {target.name}에게 {damage} 피해!"

class HealSkill(Skill):
    def use(self, caster: 'Character', target: 'Character') -> str:
        if caster.mana < self.mana_cost:
            return f"{caster.name}의 마나가 부족합니다!"
        
        caster.mana -= self.mana_cost
        heal_amount = self.damage  # damage 대신 힐량으로 사용
        target.heal(heal_amount)
        return f"{caster.name}의 {self.name}! {target.name}의 체력 {heal_amount} 회복!"

class Character(ABC):
    def __init__(self, name: str, character_class: CharacterClass):
        self.name = name
        self.character_class = character_class
        self.max_hp = 100
        self.hp = 100
        self.max_mana = 50
        self.mana = 50
        self.skills: List[Skill] = []
        self.level = 1
        self.exp = 0
    
    def add_skill(self, skill: Skill):
        self.skills.append(skill)
    
    def take_damage(self, damage: int):
        self.hp = max(0, self.hp - damage)
        if self.hp == 0:
            print(f"[X] {self.name} 쓰러짐!")
    
    def heal(self, amount: int):
        self.hp = min(self.max_hp, self.hp + amount)
    
    def is_alive(self) -> bool:
        return self.hp > 0
    
    @abstractmethod
    def get_base_stats(self) -> Dict[str, int]:
        pass
    
    def get_status(self) -> str:
        return f"{self.name} ({self.character_class.value}) Lv.{self.level} - HP: {self.hp}/{self.max_hp}, MP: {self.mana}/{self.max_mana}"

class Warrior(Character):
    def __init__(self, name: str):
        super().__init__(name, CharacterClass.WARRIOR)
        self.max_hp = 150  # 전사는 체력이 높음
        self.hp = 150
        self.max_mana = 30  # 마나는 낮음
        self.mana = 30
        
        # 전사 스킬
        self.add_skill(AttackSkill("검 베기", 25, 5))
        self.add_skill(AttackSkill("파워 어택", 40, 15))
    
    def get_base_stats(self) -> Dict[str, int]:
        return {"attack": 20, "defense": 15, "magic": 5}

class Mage(Character):
    def __init__(self, name: str):
        super().__init__(name, CharacterClass.MAGE)
        self.max_hp = 80  # 마법사는 체력이 낮음
        self.hp = 80
        self.max_mana = 100  # 마나는 높음
        self.mana = 100
        
        # 마법사 스킬
        self.add_skill(AttackSkill("파이어볼", 35, 20))
        self.add_skill(AttackSkill("라이트닝", 45, 30))
    
    def get_base_stats(self) -> Dict[str, int]:
        return {"attack": 10, "defense": 5, "magic": 25}

class Healer(Character):
    def __init__(self, name: str):
        super().__init__(name, CharacterClass.HEALER)
        self.max_mana = 80
        self.mana = 80
        
        # 힐러 스킬
        self.add_skill(HealSkill("힐", 30, 15))
        self.add_skill(AttackSkill("홀리 라이트", 20, 10))
    
    def get_base_stats(self) -> Dict[str, int]:
        return {"attack": 12, "defense": 10, "magic": 18}

# 게임 시스템
class BattleSystem:
    MAX_TURNS = 30   # 서로 회복만 하며 끝나지 않는 전투를 막기 위한 턴 제한
    MANA_REGEN = 10  # 턴마다 회복하는 마나

    def __init__(self):
        self.turn_count = 0
    
    def start_battle(self, team1: List[Character], team2: List[Character]):
        print("전투 시작!")
        self.turn_count = 0
        
        while self._has_alive_members(team1) and self._has_alive_members(team2):
            if self.turn_count >= self.MAX_TURNS:
                print(f"\n{self.MAX_TURNS}턴이 지나 무승부!")
                return
            self.turn_count += 1
            print(f"\n--- 턴 {self.turn_count} ---")
            
            # 팀1 턴
            self._execute_team_turn(team1, team2, "팀1")
            if not self._has_alive_members(team2):
                break
            
            # 팀2 턴
            self._execute_team_turn(team2, team1, "팀2")
        
        # 승부 결과
        if self._has_alive_members(team1):
            print("팀1 승리!")
        else:
            print("팀2 승리!")
    
    def _has_alive_members(self, team: List[Character]) -> bool:
        return any(char.is_alive() for char in team)
    
    def _execute_team_turn(self, attacking_team: List[Character], 
                          defending_team: List[Character], team_name: str):
        print(f"\n{team_name}의 턴:")
        
        for attacker in attacking_team:
            if not attacker.is_alive():
                continue
            
            # 매 턴 마나를 조금씩 회복 (회복이 없으면 마나가 바닥난 뒤 아무도 공격하지 못한다)
            attacker.mana = min(attacker.max_mana, attacker.mana + self.MANA_REGEN)
            
            # 살아있는 적 중 랜덤 선택
            alive_enemies = [char for char in defending_team if char.is_alive()]
            if not alive_enemies:
                break
            
            target = random.choice(alive_enemies)
            
            # 스킬 중 랜덤 선택
            if attacker.skills:
                skill = random.choice(attacker.skills)
                if isinstance(skill, HealSkill):
                    # 회복 스킬은 적이 아니라 체력이 가장 낮은 아군에게 쓴다
                    alive_allies = [char for char in attacking_team if char.is_alive()]
                    target = min(alive_allies, key=lambda char: char.hp)
                result = skill.use(attacker, target)
                print(f"  {result}")
            
            # 상태 출력
            print(f"  → {target.get_status()}")

# 테스트 실행
if __name__ == "__main__":
    # 팀 구성
    team1 = [
        Warrior("아서"),
        Mage("멀린")
    ]
    
    team2 = [
        Warrior("골리앗"),
        Healer("엘리사")
    ]
    
    # 전투 시작
    battle = BattleSystem()
    battle.start_battle(team1, team2)
