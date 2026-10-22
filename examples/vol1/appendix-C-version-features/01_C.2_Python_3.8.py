"""1권 부록 C. 버전별 새 기능 (3.8~3.14) — C.2 Python 3.8

원고: manuscript/appendix/C-version-features.md (39줄부터)
"""

# ---- 원고 39줄 ----
# Python 3.8 이상
data = [3, 8, 1, 9]
if (n := len(data)) > 3:
    print(f"원소가 {n}개라 너무 많아요")  # 원소가 4개라 너무 많아요

def divide(a, b, /):          # a, b는 위치로만 넘길 수 있음
    return a / b
print(divide(6, 3))           # 2.0

x, items = 3, ["a", "b"]
print(f"{x=}, {len(items)=}")  # x=3, len(items)=2

import math
print(math.prod([2, 3, 4]), math.isqrt(10))  # 24 3
