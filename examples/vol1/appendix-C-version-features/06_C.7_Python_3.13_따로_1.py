"""1권 부록 C. 버전별 새 기능 (3.8~3.14) — C.7 Python 3.13

원고: manuscript/appendix/C-version-features.md (280줄부터)
"""

# ---- 원고 280줄 ----
# Python 3.13 이상
import copy
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    theme: str
    size: int

base = Settings("light", 12)
print(copy.replace(base, size=14))   # Settings(theme='light', size=14)

import sys
print(sys._is_gil_enabled())         # True
