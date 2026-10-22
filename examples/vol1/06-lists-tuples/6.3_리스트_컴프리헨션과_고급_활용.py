"""1권 Chapter 6: 리스트와 튜플 — 6.3 리스트 컴프리헨션과 고급 활용

원고: manuscript/chapters/06-lists-tuples.md (251줄부터)
"""

# ---- 원고 251줄 ----
# 기존 방식
squares = []
for i in range(1, 11):
    squares.append(i ** 2)

# 리스트 컴프리헨션
squares = [i ** 2 for i in range(1, 11)]
print(f"제곱수들: {squares}")

# 한글 이름에서 성씨만 추출
full_names = ["김철수", "이영희", "박민수", "최지영", "정수진"]
surnames = [name[0] for name in full_names]
print(f"성씨들: {surnames}")

# 조건부 리스트 컴프리헨션
ages = [25, 17, 30, 16, 45, 19, 35]
adults = [age for age in ages if age >= 20]
print(f"성인 나이: {adults}")

# if-else 표현식
age_groups = ["성인" if age >= 20 else "미성년" for age in ages]
print(f"연령대: {age_groups}")

# ---- 원고 282줄 ----
# 구구단 만들기
multiplication_table = [[i * j for j in range(1, 10)] for i in range(2, 10)]
print("구구단 2단:")
print(multiplication_table[0])

# 행렬 전치
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
transposed = [[row[i] for row in matrix] for i in range(len(matrix[0]))]
print(f"원본 행렬: {matrix}")
print(f"전치 행렬: {transposed}")

# 단어별로 한글 음절만 골라내기
words = ["안녕", "하세요", "파이썬"]
syllables = [[char for char in word if ord(char) >= 0xAC00] for word in words]
print(f"한글 문자들: {syllables}")
