"""1권 부록 B. 한눈에 보는 파이썬 — B.7 리스트와 튜플 (6장)

원고: manuscript/appendix/B-cheatsheet.md (301줄부터)
"""

# ---- 원고 301줄 ----
a = [3, 1, 2]
print(a.sort(), a)                       # None [1, 2, 3]
words = ["banana", "Apple", "cherry"]
print(sorted(words))                     # ['Apple', 'banana', 'cherry']
print(sorted(words, key=str.lower))      # ['Apple', 'banana', 'cherry']
print(sorted(words, key=len, reverse=True))  # ['banana', 'cherry', 'Apple']
people = [("민수", 30), ("지아", 25)]
print(sorted(people, key=lambda p: p[1]))    # [('지아', 25), ('민수', 30)]

# ---- 원고 314줄 ----
point = (3, 4)
x, y = point                  # 풀기(언패킹)
print(x, y, point.count(3))   # 3 4 1
print({(0, 0): "원점"}[(0, 0)])  # 원점
