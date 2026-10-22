"""1권 Chapter 14: 모듈과 패키지 — 14.1 모듈의 기본 개념

원고: manuscript/chapters/14-modules-packages.md (32줄부터)
"""

# ---- 원고 32줄 ----
import random

번호 = sorted(random.sample(range(1, 46), 6))
print(f"이번 주 로또 번호: {번호}")

# ---- 원고 128줄 ----
import keyword

print(keyword.kwlist)       # 예약어
print(keyword.softkwlist)   # soft keyword
