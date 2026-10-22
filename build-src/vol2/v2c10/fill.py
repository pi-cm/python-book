"""template.md의 <<CODE x>>/<<OUT x>>를 실제 코드와 실행 출력으로 채운다. (10장: torchvision 추가, 데이터·가중치 캐시를 scratchpad로)"""
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

D = Path(sys.argv[1]).resolve(); dst = Path(sys.argv[2])
ONLY = set(sys.argv[3:])      # 이름을 주면 그 블록만 실행해 출력 확인(원고는 쓰지 않음)
NOISE = re.compile(r"conversion_method_template|^\s*cpu = ")
ENV = dict(os.environ, TORCH_HOME=str(D.parent / "torchhub"), HF_HOME=str(D.parent / "hf"))
t = (D / "template.md").read_text(encoding="utf-8")
outs = {}
도구 = (D / "전이도구.py").read_text(encoding="utf-8")
for name in sorted(set(re.findall(r"<<(?:CODE|OUT) (\w+)>>", t))):
    if ONLY and name not in ONLY:
        continue
    src = (D / f"{name}.py").read_text(encoding="utf-8").rstrip("\n")
    # 코드가 그대로면 앞서 실행한 출력을 다시 쓴다(MPS 결과가 실행마다 조금씩 달라서 본문 수치를 고정하려고)
    캐시 = D / "cache" / f"{name}.{hashlib.sha256((src + 도구).encode()).hexdigest()[:12]}.out"
    if 캐시.exists() and not ONLY:
        out = 캐시.read_text(encoding="utf-8")
        t = t.replace(f"<<CODE {name}>>", f"```python\n{src}\n```")
        t = t.replace(f"<<OUT {name}>>", f"```text\n{out}\n```")
        outs[name] = out
        continue
    r = subprocess.run(["uv", "run", "-q", "--no-project", "--python", "3.12", "--with", "torch", "--with", "numpy",
                        "--with", "torchvision", "python", "-W", "ignore", str(D / f"{name}.py")],
                       capture_output=True, text=True, cwd=str(D.parent), env=ENV)
    if r.returncode != 0:
        sys.exit(f"{name} 실패:\n{r.stderr}")
    out = "\n".join(l for l in r.stdout.splitlines() if not NOISE.search(l))
    캐시.parent.mkdir(exist_ok=True)
    캐시.write_text(out, encoding="utf-8")
    if ONLY:
        print(f"== {name}\n{out}")
        continue
    t = t.replace(f"<<CODE {name}>>", f"```python\n{src}\n```")
    t = t.replace(f"<<OUT {name}>>", f"```text\n{out}\n```")
    outs[name] = out
if not ONLY:
    assert "<<" not in t
    dst.write_text(t, encoding="utf-8")
    print("blocks:", len(outs))
