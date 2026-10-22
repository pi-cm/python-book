import re, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from terms import KO, EN
from find import 본문
found = json.load(open(Path(__file__).parent/"found.json"))
for 용어, 영문, 뜻, 말들 in KO + EN:
    말들 = 말들 or [용어]; a, b = found[용어]
    n = b if b is not None else a
    t = 본문[n]
    for 말 in 말들:
        m = re.search(r"\*\*[^*\n]{0,15}" + re.escape(말), t) if b is not None else None
        if m is None: m = re.search(re.escape(말), t)
        if m: break
    s = t[max(0, m.start()-25): m.end()+35].replace("\n", " ")
    print(f"{용어} [{n}{'b' if b else ''}|{a}] {s}")
