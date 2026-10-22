"""1권 부록 B. 한눈에 보는 파이썬 — B.18 타입 힌트 (2장)

원고: manuscript/appendix/B-cheatsheet.md (831줄부터)
"""

# ---- 원고 831줄 ----
from typing import Optional

def find(names: list[str], target: str) -> int | None:
    return names.index(target) if target in names else None

scores: dict[str, int] = {"민수": 90}
pair: tuple[int, str] = (1, "a")
maybe: Optional[int] = None       # int | None 과 같음
print(find(["a", "b"], "b"), find([], "x"))   # 1 None
