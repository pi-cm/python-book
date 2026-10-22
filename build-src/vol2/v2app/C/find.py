"""용어마다 처음 등장한 장(코드 블록 밖 본문)과 처음 굵게 소개된 장을 찾는다."""
import re, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from terms import KO, EN
CH = Path("/Users/changmin/git/python-book/manuscript-vol2/chapters")
본문 = {}
for f in sorted(CH.glob("*.md")):
    n = int(f.name[:2]); 줄들=[]; 코드=False
    for 줄 in f.read_text(encoding="utf-8").splitlines():
        if 줄.startswith("```"): 코드 = not 코드; continue
        if not 코드: 줄들.append(줄)
    본문[n] = "\n".join(줄들)
def 찾기(말들):
    처음 = 굵게 = None
    for n, t in 본문.items():
        for 말 in 말들:
            if 처음 is None and 말 in t: 처음 = n
            if 굵게 is None and re.search(r"\*\*[^*\n]{0,15}" + re.escape(말), t): 굵게 = n
    return 처음, 굵게
결과 = {}
for 용어, 영문, 뜻, 말들 in KO + EN:
    말들 = 말들 or [용어]
    결과[용어] = 찾기(말들)
json.dump(결과, open(Path(__file__).parent / "found.json", "w"), ensure_ascii=False, indent=0)
for k, (a, b) in 결과.items():
    if a is None or (b is not None and b != a):
        print(f"{k}: 처음 {a}, 굵게 {b}")
print(len(결과))
