"""1권 Chapter 11: 객체 지향 프로그래밍 — 11.5 실습 문제

원고: manuscript/chapters/11-object-oriented-programming.md (1073줄부터)
"""

# ---- 원고 1073줄 ----
# 1번: 기본 클래스 정의
class Book:
    def __init__(self, title: str, author: str, pages: int):
        # 문제: 책 클래스의 초기화 메서드를 완성하세요
        pass

# 답:
class Book:
    def __init__(self, title: str, author: str, pages: int):
        self.title = title
        self.author = author
        self.pages = pages
        self.is_borrowed = False
    
    def borrow(self):
        if not self.is_borrowed:
            self.is_borrowed = True
            return f"'{self.title}' 대출되었습니다"
        return "이미 대출된 책입니다"
    
    def return_book(self):
        if self.is_borrowed:
            self.is_borrowed = False
            return f"'{self.title}' 반납되었습니다"
        return "대출되지 않은 책입니다"

book = Book("파이썬 완전정복", "김개발", 500)
print(book.borrow())

# 2번: 프로퍼티 활용
class Temperature:
    def __init__(self, celsius: float = 0):
        self._celsius = celsius
    
    # 문제: 화씨온도 프로퍼티를 추가하세요
    pass

# 답:
class Temperature:
    def __init__(self, celsius: float = 0):
        self._celsius = celsius
    
    @property
    def celsius(self):
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("절대영도보다 낮을 수 없습니다")
        self._celsius = value
    
    @property
    def fahrenheit(self):
        return self._celsius * 9/5 + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        self.celsius = (value - 32) * 5/9

temp = Temperature(25)
print(f"{temp.celsius}°C = {temp.fahrenheit}°F")

# 3번: 상속 구현
class Animal:
    def __init__(self, name: str):
        self.name = name
    
    def speak(self):
        pass

class Dog(Animal):
    # 문제: Dog 클래스에서 speak 메서드를 오버라이드하세요
    pass

# 답:
class Dog(Animal):
    def __init__(self, name: str, breed: str):
        super().__init__(name)
        self.breed = breed
    
    def speak(self):
        return f"{self.name}: 멍멍!"

class Cat(Animal):
    def speak(self):
        return f"{self.name}: 야옹~"

dog = Dog("바둑이", "진돗개")
cat = Cat("나비")
print(dog.speak())
print(cat.speak())

# 4번: 클래스 메서드 활용
class Student:
    student_count = 0
    
    def __init__(self, name: str, grade: int):
        self.name = name
        self.grade = grade
        Student.student_count += 1
    
    # 문제: 총 학생 수를 반환하는 클래스 메서드를 만드세요
    pass

# 답:
class Student:
    student_count = 0
    
    def __init__(self, name: str, grade: int):
        self.name = name
        self.grade = grade
        Student.student_count += 1
    
    @classmethod
    def get_student_count(cls):
        return cls.student_count
    
    @classmethod
    def create_elementary_student(cls, name: str):
        return cls(name, 1)

s1 = Student("김철수", 3)
s2 = Student.create_elementary_student("이영희")
print(f"총 학생 수: {Student.get_student_count()}")

# 5번: 특수 메서드 구현
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    # 문제: 두 점 사이의 거리를 계산하는 특수 메서드들을 추가하세요
    pass

# 답:
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"({self.x}, {self.y})"
    
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def distance_to(self, other):
        return ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5

p1 = Point(1, 2)
p2 = Point(3, 4)
print(f"p1: {p1}")
print(f"p1 + p2: {p1 + p2}")
print(f"거리: {p1.distance_to(p2):.2f}")
