"""template.md의 <<CODE x>>/<<OUT x>>를 실제 코드와 실행 출력으로 채운다. (15장: 그림은 run/ 에서 만들어 assets로 복사)"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

D = Path(sys.argv[1]); dst = Path(sys.argv[2])
ONLY = set(sys.argv[3:])                 # 이름을 주면 그 블록만 다시 실행하고 나머지는 캐시 사용
RUN = D / "run"; CACHE = D / "cache"; CACHE.mkdir(exist_ok=True)
IMG = Path("/Users/changmin/git/python-book/manuscript-vol2/assets/images/ch15")
NOISE = re.compile(r"conversion_method_template|^\s*cpu = ")
t = (D / "template.md").read_text(encoding="utf-8")
outs = {}
for name in sorted(set(re.findall(r"<<(?:CODE|OUT) (\w+)>>", t))):
    src = (D / f"{name}.py").read_text(encoding="utf-8").rstrip("\n")
    c = CACHE / f"{name}.out"
    if ONLY and name not in ONLY and c.exists():
        out = c.read_text(encoding="utf-8")
    else:
        r = subprocess.run(["uv", "run", "-q", "--no-project", "--python", "3.12", "--with", "torch", "--with", "numpy",
                            "--with", "torchvision", "--with", "matplotlib",
                            "python", "-W", "ignore", str(D / f"{name}.py")],
                           capture_output=True, text=True, cwd=str(RUN))
        if r.returncode != 0:
            sys.exit(f"{name} 실패:\n{r.stderr}")
        out = "\n".join(l for l in r.stdout.splitlines() if not NOISE.search(l))
        c.write_text(out, encoding="utf-8")
        print("ran", name, flush=True)
    t = t.replace(f"<<CODE {name}>>", f"```python\n{src}\n```")
    t = t.replace(f"<<OUT {name}>>", f"```text\n{out}\n```")
    outs[name] = out
assert "<<" not in t
for p in RUN.glob("*.png"):
    shutil.copy(p, IMG / p.name)
dst.write_text(t, encoding="utf-8")
print("blocks:", len(outs))
