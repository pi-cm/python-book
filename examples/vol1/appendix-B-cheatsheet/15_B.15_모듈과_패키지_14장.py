"""1권 부록 B. 한눈에 보는 파이썬 — B.15 모듈과 패키지 (14장)

원고: manuscript/appendix/B-cheatsheet.md (723줄부터)
"""

# ---- 원고 723줄 ----
import math                       # 모듈 통째로
import datetime as dt             # 별명
from pathlib import Path          # 필요한 것만
from collections import Counter, deque

print(math.sqrt(16), dt.date(2026, 1, 1).year)  # 4.0 2026
