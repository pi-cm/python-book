"""1권 Chapter 9: 함수 — 9.1 함수 정의와 호출

원고: manuscript/chapters/09-functions.md (52줄부터)
"""

# ---- 원고 52줄 ----
# 수학의 f(x) = 3x + 2를 파이썬으로
def f(x):
    return 3 * x + 2

print(f(2))  # 8

# return이 없는 함수
def say_hello():
    print("안녕하세요!")

result = say_hello()  # 안녕하세요!
print(result)         # None

# ---- 원고 82줄 ----
def make_profile(name, age, city, job, hobby):
    return f"{name}({age}) / {city} / {job} / 취미: {hobby}"

# 위치 인자: 순서가 곧 의미입니다
print(make_profile("김철수", 25, "서울", "개발자", "등산"))
print(make_profile("김철수", "서울", 25, "등산", "개발자"))  # 순서가 꼬였어요!

# 키워드 인자: 이름표를 붙이면 순서는 상관없어요
print(make_profile(hobby="등산", job="개발자", name="김철수", city="서울", age=25))

# ---- 원고 107줄 ----
# 정의할 때의 * : 여러 인자를 튜플 하나로 묶기(packing)
def my_sum(*numbers):
    print(f"받은 값: {numbers}")
    return sum(numbers)

print(my_sum(1, 2, 3))        # 받은 값: (1, 2, 3) → 6

# 호출할 때의 * : 리스트를 풀어서 하나씩 넘기기(unpacking)
nums = [1, 2, 3, 4, 5]
print(my_sum(*nums))          # my_sum(1, 2, 3, 4, 5)와 같아요 → 15

# ** : 키워드 인자를 딕셔너리 하나로 묶기
def show_info(**info):
    print(info)

show_info(name="김철수", age=25)  # {'name': '김철수', 'age': 25}

# 함수 밖에서도 됩니다
first, *rest = [10, 20, 30, 40]
print(first, rest)            # 10 [20, 30, 40]

# ---- 원고 138줄 ----
def contains(matrix, target):
    for row in matrix:
        for value in row:
            if value == target:
                return True   # 찾자마자 두 반복문을 한꺼번에 빠져나갑니다
    return False

matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
print(contains(matrix, 5))   # True
print(contains(matrix, 10))  # False

# ---- 원고 157줄 ----
def add_one(number):
    number = number + 1        # 새 정수 객체를 만들어 이름표만 옮깁니다
    print(f"함수 안: {number}")

def add_item(items):
    items.append(4)            # 들어온 리스트 객체 자체를 고칩니다
    print(f"함수 안: {items}")

n = 10
add_one(n)                     # 함수 안: 11
print(f"함수 밖: {n}")         # 함수 밖: 10

my_list = [1, 2, 3]
add_item(my_list)              # 함수 안: [1, 2, 3, 4]
print(f"함수 밖: {my_list}")   # 함수 밖: [1, 2, 3, 4]
