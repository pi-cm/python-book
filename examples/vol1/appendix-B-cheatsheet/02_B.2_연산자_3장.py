"""1권 부록 B. 한눈에 보는 파이썬 — B.2 연산자 (3장)

원고: manuscript/appendix/B-cheatsheet.md (78줄부터)
"""

# ---- 원고 78줄 ----
print(divmod(17, 5))               # (3, 2)
print(0.1 + 0.2 == 0.3)            # False
import math
print(math.isclose(0.1 + 0.2, 0.3))  # True
print(None or [] or "마지막")       # 마지막
print(3 and 0 and 5)               # 0
