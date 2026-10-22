"""template.md의 <<CODE x>>/<<OUT x>>를 실제 코드와 실행 출력으로 채운다."""
import re
import subprocess
import sys
from pathlib import Path

D = Path(sys.argv[1]); dst = Path(sys.argv[2])
NOISE = re.compile(r"conversion_method_template|^\s*cpu = ")
t = (D / "template.md").read_text(encoding="utf-8")
outs = {}
for name in sorted(set(re.findall(r"<<(?:CODE|OUT) (\w+)>>", t))):
    src = (D / f"{name}.py").read_text(encoding="utf-8").rstrip("\n")
    r = subprocess.run(["uv", "run", "-q", "--no-project", "--python", "3.12", "--with", "torch", "--with", "numpy", "--with", "statsmodels", "--with", "pandas", "--with", "matplotlib",
                        "python", "-W", "ignore", str(D / f"{name}.py")],
                       capture_output=True, text=True, cwd=str(D / "run"))
    if r.returncode != 0:
        sys.exit(f"{name} 실패:\n{r.stderr}")
    out = "\n".join(l for l in r.stdout.splitlines() if not NOISE.search(l))
    t = t.replace(f"<<CODE {name}>>", f"```python\n{src}\n```")
    t = t.replace(f"<<OUT {name}>>", f"```text\n{out}\n```")
    outs[name] = out
assert "<<" not in t
dst.write_text(t, encoding="utf-8")
print("blocks:", len(outs))
# 그림은 원고 그림 폴더로 옮긴다
import shutil
그림 = Path("/Users/changmin/git/python-book/manuscript-vol2/assets/images/ch11")
for p in (D / "run").glob("*.png"):
    shutil.copy(p, 그림 / p.name)
