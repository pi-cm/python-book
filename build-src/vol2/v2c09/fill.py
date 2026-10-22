"""template.md의 <<CODE x>>/<<OUT x>>를 실제 코드와 실행 출력으로 채운다 (9장용: torchvision·scikit-learn·matplotlib 추가, 그림 복사)."""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

D = Path(sys.argv[1]); dst = Path(sys.argv[2])
RUN = D / "run"                                   # data -> scratchpad/data 링크가 있는 실행 폴더
IMG = Path("/Users/changmin/git/python-book/manuscript-vol2/assets/images/ch09")
NOISE = re.compile(r"conversion_method_template|^\s*cpu = ")
env = dict(os.environ, HF_HOME=str(D.parent / "hf"))
t = (D / "template.md").read_text(encoding="utf-8")
outs = {}
only = set(sys.argv[3:])                          # 이름을 주면 그 블록만 실행해 보기
for name in sorted(set(re.findall(r"<<(?:CODE|OUT) (\w+)>>", t))):
    if only and name not in only:
        continue
    src = (D / f"{name}.py").read_text(encoding="utf-8").rstrip("\n")
    r = subprocess.run(["uv", "run", "-q", "--no-project", "--python", "3.12", "--with", "torch", "--with", "numpy",
                        "--with", "torchvision", "--with", "scikit-learn", "--with", "matplotlib",
                        "python", "-W", "ignore", str(D / f"{name}.py")],
                       capture_output=True, text=True, cwd=str(RUN), env=env)
    if r.returncode != 0:
        sys.exit(f"{name} 실패:\n{r.stderr}")
    out = "\n".join(l for l in r.stdout.splitlines() if not NOISE.search(l))
    (D / "outs").mkdir(exist_ok=True)
    (D / "outs" / f"{name}.txt").write_text(out, encoding="utf-8")
    print(f"[{name}] 완료", flush=True)
    t = t.replace(f"<<CODE {name}>>", f"```python\n{src}\n```")
    t = t.replace(f"<<OUT {name}>>", f"```text\n{out}\n```")
    outs[name] = out
if only:
    sys.exit(0)
assert "<<" not in t
for png in RUN.glob("*.png"):
    shutil.copy(png, IMG / png.name)
dst.write_text(t, encoding="utf-8")
print("blocks:", len(outs))
