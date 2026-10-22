"""1권 부록 B. 한눈에 보는 파이썬 — B.4 f-string 서식 (2장)

원고: manuscript/appendix/B-cheatsheet.md (181줄부터)
"""

# ---- 원고 181줄 ----
from datetime import date
x, name, d = 10, "파이썬", date(2026, 10, 21)
print(f"{x=}, {x * 2 = }")          # x=10, x * 2 = 20
print(f"[{name:^8}]")               # [  파이썬   ]
print(f"{1234567:,}원 {0.256:.1%}")  # 1,234,567원 25.6%
print(f"{d:%Y년 %m월 %d일}")         # 2026년 10월 21일
w = 8
print(f"[{3.14159:>{w}.2f}]")       # [    3.14]
