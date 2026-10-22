"""1권 부록 B. 한눈에 보는 파이썬 — B.14 파일 (12장)

원고: manuscript/appendix/B-cheatsheet.md (666줄부터)
"""

# ---- 원고 666줄 ----
from pathlib import Path

p = Path("memo.txt")
p.write_text("첫 줄\n둘째 줄\n", encoding="utf-8")

with open(p, encoding="utf-8") as f:     # 블록이 끝나면 자동으로 닫힘
    for line in f:
        print(line.rstrip())             # 첫 줄 / 둘째 줄

with open(p, "a", encoding="utf-8") as f:
    f.write("셋째 줄\n")

print(p.read_text(encoding="utf-8").splitlines())  # ['첫 줄', '둘째 줄', '셋째 줄']
print(p.exists(), p.suffix, p.stem)      # True .txt memo
p.unlink()                               # 파일 지우기

# ---- 원고 706줄 ----
import csv, io, json

data = {"이름": "민수", "점수": [90, 85]}
text = json.dumps(data, ensure_ascii=False)
print(text)                        # {"이름": "민수", "점수": [90, 85]}
print(json.loads(text)["점수"][0])  # 90

buf = io.StringIO()
writer = csv.writer(buf)
writer.writerow(["이름", "점수"])
writer.writerow(["민수", 90])
print(buf.getvalue().splitlines())  # ['이름,점수', '민수,90']
