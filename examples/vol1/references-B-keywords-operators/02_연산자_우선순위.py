"""1권 레퍼런스 B. 키워드와 연산자 — 연산자 우선순위

원고: manuscript/references/B-keywords-operators.md (197줄부터)
"""

# ---- 원고 197줄 ----
print(10 - 5 - 2)          # 3
print(2 ** 3 ** 2)         # 512
print(-2 ** 2, 2 ** -1)    # -4 0.5
print(1 < 3 > 2)           # True
x = 0
print('양' if x > 0 else '음' if x < 0 else '영')   # 영
print(6 & 1 == 0)          # True
