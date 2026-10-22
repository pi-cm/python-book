"""1권 부록 C. 버전별 새 기능 (3.8~3.14) — C.3 Python 3.9

원고: manuscript/appendix/C-version-features.md (72줄부터)
"""

# ---- 원고 72줄 ----
# Python 3.9 이상
defaults = {"theme": "light", "lang": "ko"}
user = {"theme": "dark"}
print(defaults | user)                # {'theme': 'dark', 'lang': 'ko'}

print("unhappy".removeprefix("un"))   # happy
print("report.csv".removesuffix(".csv"))  # report

def total(scores: dict[str, list[int]]) -> dict[str, int]:
    return {name: sum(s) for name, s in scores.items()}
print(total({"민수": [90, 80]}))       # {'민수': 170}

from zoneinfo import ZoneInfo
from datetime import datetime
seoul = datetime(2026, 10, 21, 9, 0, tzinfo=ZoneInfo("Asia/Seoul"))
print(seoul.astimezone(ZoneInfo("UTC")))  # 2026-10-21 00:00:00+00:00
