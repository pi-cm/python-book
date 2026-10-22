"""1권 부록 D. 자주 만나는 오류와 해결 — D.6 모듈, 파일, 재귀

원고: manuscript/appendix/D-troubleshooting.md (609줄부터)
"""

# ---- 원고 609줄 ----
from pathlib import Path

BASE = Path(__file__).parent        # 이 스크립트가 있는 폴더
data_file = BASE / "data.txt"
print(data_file.exists())
