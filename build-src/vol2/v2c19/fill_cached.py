"""본문만 고쳤을 때: 직전 fill.py 실행이 outs/에 남긴 실제 출력으로 template.md를 다시 채운다."""
import re
import sys
from pathlib import Path

D = Path(sys.argv[1]); dst = Path(sys.argv[2])
t = (D / "template.md").read_text(encoding="utf-8")
for name in sorted(set(re.findall(r"<<(?:CODE|OUT) (\w+)>>", t))):
    src = (D / f"{name}.py").read_text(encoding="utf-8").rstrip("\n")
    out = (D / "outs" / f"{name}.txt").read_text(encoding="utf-8")
    t = t.replace(f"<<CODE {name}>>", f"```python\n{src}\n```")
    t = t.replace(f"<<OUT {name}>>", f"```text\n{out}\n```")
assert "<<" not in t
dst.write_text(t, encoding="utf-8")
print("ok")
