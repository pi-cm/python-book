import sys, unicodedata, re
from pathlib import Path
def w(s): return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)
lim=int(sys.argv[1])
for f in sys.argv[2:]:
    t=Path(f).read_text()
    if f.endswith(".md"):
        lines=[]; inb=False
        for l in t.splitlines():
            if l.startswith("```python"): inb=True; continue
            if l.startswith("```"): inb=False; continue
            if inb: lines.append(l)
    else: lines=t.splitlines()
    for i,l in enumerate(lines):
        if w(l)>lim: print(f"{Path(f).name}:{i+1}: {w(l)}: {l}")
