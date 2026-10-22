"""1권 부록 B. 한눈에 보는 파이썬 — B.8 딕셔너리와 집합 (7장)

원고: manuscript/appendix/B-cheatsheet.md (339줄부터)
"""

# ---- 원고 339줄 ----
d = {"a": 1, "b": 2}
print(d.get("z"), d.get("z", 0))          # None 0
print(d | {"b": 20, "c": 3})              # {'a': 1, 'b': 20, 'c': 3}
for k, v in d.items():
    print(k, v)                           # a 1 / b 2
print(dict(zip(["x", "y"], [1, 2])))      # {'x': 1, 'y': 2}
print(max(d, key=d.get))                  # b

# ---- 원고 363줄 ----
a, b = {1, 2, 3}, {2, 3, 4}
print(a | b, a & b, a - b, a ^ b)   # {1, 2, 3, 4} {2, 3} {1} {1, 4}
print(list(dict.fromkeys([3, 1, 3, 2, 1])))  # [3, 1, 2]
