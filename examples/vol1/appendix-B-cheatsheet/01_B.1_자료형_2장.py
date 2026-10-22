"""1권 부록 B. 한눈에 보는 파이썬 — B.1 자료형 (2장)

원고: manuscript/appendix/B-cheatsheet.md (30줄부터)
"""

# ---- 원고 30줄 ----
falsy = [False, None, 0, 0.0, 0j, "", [], (), {}, set(), range(0)]
print(all(not bool(v) for v in falsy))  # True
print(bool("0"), bool([0]), bool(" "))  # True True True

# ---- 원고 40줄 ----
x = 3.7
print(type(x).__name__)            # float
print(isinstance(x, (int, float))) # True
print(int(x), round(x), round(2.5))  # 3 4 2
print(int("0b101", 0), int("12", 8))  # 5 10
print(float("1e3"), str(1/3)[:6])  # 1000.0 0.3333

# ---- 원고 53줄 ----
a, b = 1, 2
a, b = b, a                 # 값 맞바꾸기
first, *rest = [1, 2, 3, 4]
print(a, b, first, rest)    # 2 1 1 [2, 3, 4]
x = y = 0                   # 같은 객체에 이름 두 개
print(x is y)               # True
