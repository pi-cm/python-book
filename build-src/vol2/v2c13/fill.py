"""template.md의 <<CODE x>>/<<OUT x>>를 실제 코드와 실행 출력으로 채운다."""
import re
import subprocess
import sys
from pathlib import Path

import os
D = Path(sys.argv[1]); dst = Path(sys.argv[2])
# 데이터(data/)와 HF 캐시를 스크래치 폴더로 통일한다
SCRATCH = Path("/private/tmp/claude-501/-Users-changmin-git-python-book/e14a96f2-1a68-4a7a-918b-2027747e5566/scratchpad")
ENV = {**os.environ, "HF_HOME": str(SCRATCH / "hf"), "HF_HUB_DISABLE_PROGRESS_BARS": "1",
       "TRANSFORMERS_VERBOSITY": "error", "TOKENIZERS_PARALLELISM": "false"}
import hashlib
# 오래 걸리는 미세조정 블록을 다시 돌리지 않도록, 코드(+공용 모듈)가 같으면 실제 실행 출력을 재사용한다
CACHE = D / ".cache"; CACHE.mkdir(exist_ok=True)
공용 = "".join(p.read_text(encoding="utf-8") for p in sorted(D.glob("[!b]*.py")) if p.name not in {"fill.py"})
NOISE = re.compile(r"conversion_method_template|^\s*cpu = ")
t = (D / "template.md").read_text(encoding="utf-8")
outs = {}
for name in sorted(set(re.findall(r"<<(?:CODE|OUT) (\w+)>>", t))):
    src = (D / f"{name}.py").read_text(encoding="utf-8").rstrip("\n")
    key = hashlib.sha256((src + 공용).encode()).hexdigest()[:16]
    cached = CACHE / f"{name}.{key}.out"
    if cached.exists():
        out = cached.read_text(encoding="utf-8")
        t = t.replace(f"<<CODE {name}>>", f"```python\n{src}\n```")
        t = t.replace(f"<<OUT {name}>>", f"```text\n{out}\n```")
        outs[name] = out
        continue
    r = subprocess.run(["uv", "run", "-q", "--no-project", "--python", "3.12", "--with", "torch", "--with", "numpy", "--with", "transformers", "--with", "tokenizers", "--with", "datasets", "--with", "kiwipiepy", "--with", "scikit-learn",
                        "python", "-W", "ignore", str(D / f"{name}.py")],
                       capture_output=True, text=True, cwd=str(SCRATCH), env=ENV)
    if r.returncode != 0:
        sys.exit(f"{name} 실패:\n{r.stderr}")
    out = "\n".join(l for l in r.stdout.splitlines() if not NOISE.search(l))
    t = t.replace(f"<<CODE {name}>>", f"```python\n{src}\n```")
    t = t.replace(f"<<OUT {name}>>", f"```text\n{out}\n```")
    outs[name] = out
    cached.write_text(out, encoding="utf-8")
    print(name, "ok", flush=True)
assert "<<" not in t
dst.write_text(t, encoding="utf-8")
print("blocks:", len(outs))
