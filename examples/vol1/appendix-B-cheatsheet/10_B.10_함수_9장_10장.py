"""1권 부록 B. 한눈에 보는 파이썬 — B.10 함수 (9장, 10장)

원고: manuscript/appendix/B-cheatsheet.md (418줄부터)
"""

# ---- 원고 418줄 ----
def greet(name, greeting="안녕하세요", *args, sep=" ", **kwargs):
    """인사말을 만든다."""
    return sep.join([greeting, name, *args]) + str(kwargs or "")

print(greet("민수"))                      # 안녕하세요 민수
print(greet("민수", "반가워요", "님"))       # 반가워요 민수 님
print(greet("민수", sep="-", mood="good"))  # 안녕하세요-민수{'mood': 'good'}

# ---- 원고 438줄 ----
def area(w, h, /, *, unit="cm"):
    return f"{w * h}{unit}²"

print(area(3, 4))             # 12cm²
print(area(3, 4, unit="m"))   # 12m²
size = (5, 6)
print(area(*size))            # 30cm²

# ---- 원고 450줄 ----
count = 0
def inc():
    global count             # 모듈의 count를 바꾸겠다
    count += 1

def make_counter():
    n = 0
    def step():
        nonlocal n           # 감싼 함수의 n을 바꾸겠다
        n += 1
        return n
    return step

inc()
c = make_counter()
c()
print(count, c())            # 1 2

# ---- 원고 472줄 ----
nums = [1, 2, 3, 4, 5]
print(list(map(lambda n: n * n, nums)))         # [1, 4, 9, 16, 25]
print(list(filter(lambda n: n % 2, nums)))      # [1, 3, 5]
from functools import reduce, partial
print(reduce(lambda a, b: a * b, nums))         # 120
double = partial(pow, exp=2)
print(double(9))                                # 81
print(any(n > 4 for n in nums), all(n > 0 for n in nums))  # True True

# ---- 원고 485줄 ----
import functools

def shout(func):
    @functools.wraps(func)          # 원래 함수의 이름·docstring 유지
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).upper()
    return wrapper

@shout
def hello(name):
    return f"hello, {name}"

print(hello("kim"), hello.__name__)  # HELLO, KIM hello

@functools.cache
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)
print(fib(80))                       # 23416728348467685
