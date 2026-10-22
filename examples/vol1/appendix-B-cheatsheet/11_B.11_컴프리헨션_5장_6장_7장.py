"""1권 부록 B. 한눈에 보는 파이썬 — B.11 컴프리헨션 (5장, 6장, 7장)

원고: manuscript/appendix/B-cheatsheet.md (515줄부터)
"""

# ---- 원고 515줄 ----
print([x * x for x in range(6) if x % 2 == 0])   # [0, 4, 16]
print(["짝" if x % 2 == 0 else "홀" for x in range(3)])  # ['짝', '홀', '짝']
print({w: len(w) for w in ["hi", "hello"]})       # {'hi': 2, 'hello': 5}
print({len(w) for w in ["a", "b", "cc"]})         # {1, 2}
print(sum(x * x for x in range(4)))               # 14
print([(i, j) for i in range(2) for j in "ab"])   # [(0, 'a'), (0, 'b'), (1, 'a'), (1, 'b')]
matrix = [[1, 2], [3, 4]]
print([n for row in matrix for n in row])         # [1, 2, 3, 4]
