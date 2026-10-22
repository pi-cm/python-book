"""단계별로 '처음 설명한 장'을 찾는다: 1) **용어( 2) **용어** 꼴 3) 본문 첫 등장."""
import re, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from terms import KO, EN
from find import 본문
def 찾기(말들):
    for 단계, 꼴 in ((1, r"\*\*{m}\s?\("), (2, r"\*\*{m}"), (3, r"{m}")):
        for n, t in 본문.items():
            for 말 in 말들:
                m = re.search(꼴.format(m=re.escape(말)), t)
                if m:
                    s = t[max(0, m.start()-30): m.end()+30].replace("\n", " ")
                    return n, 단계, s
결과 = {}
for 용어, 영문, 뜻, 말들 in KO + EN:
    결과[용어] = 찾기(말들 or [용어])
json.dump({k: v[:2] for k, v in 결과.items()}, open(Path(__file__).parent/"found2.json", "w"), ensure_ascii=False)
if __name__ == "__main__":
    for k, (n, 단계, s) in 결과.items():
        print(f"{k} [{n}/{단계}] {s}")
