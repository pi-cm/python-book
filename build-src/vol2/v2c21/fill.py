"""template.md의 <<CODE x>>/<<OUT x>>/<<FILE 경로>>를 실제 코드·실행 출력·파일 내용으로 채운다.
(21장: torch·numpy·pandas, 실행 폴더 run/)"""
import os
import re
import subprocess
import sys
from pathlib import Path

D = Path(sys.argv[1]); dst = Path(sys.argv[2])
RUN = D / "run"
NOISE = re.compile(r"conversion_method_template|^\s*cpu = ")
ENV = dict(os.environ, HF_HOME=str(D.parent / "hf"), HF_HUB_OFFLINE="1", TRANSFORMERS_VERBOSITY="error",
           HF_HUB_DISABLE_PROGRESS_BARS="1", TOKENIZERS_PARALLELISM="false", BOOK_DATA_DIR="data")
PKGS = ["torch", "numpy", "pandas"]
LANG = {".py": "python", ".toml": "toml", ".txt": "text"}
only = set(sys.argv[3:])                          # 이름을 주면 그 블록만 실행해 보기
t = (D / "template.md").read_text(encoding="utf-8")
outs = {}
for name in sorted(set(re.findall(r"<<(?:CODE|OUT) (\w+)>>", t))):
    if only and name not in only:
        continue
    src = (D / f"{name}.py").read_text(encoding="utf-8").rstrip("\n")
    캐시 = D / "outs" / f"{name}.txt"
    if os.environ.get("REUSE") and 캐시.exists():   # 문장만 고쳤을 때: 직전 실행 출력을 그대로 쓴다
        out = 캐시.read_text(encoding="utf-8")
        t = t.replace(f"<<CODE {name}>>", f"```python\n{src}\n```").replace(f"<<OUT {name}>>", f"```text\n{out}\n```")
        outs[name] = out
        continue
    cmd = ["uv", "run", "-q", "--no-project", "--python", "3.12"]
    for p in PKGS:
        cmd += ["--with", p]
    r = subprocess.run(cmd + ["python", "-W", "ignore", str(D / f"{name}.py")],
                       capture_output=True, text=True, cwd=str(RUN), env=ENV)
    if r.returncode != 0:
        sys.exit(f"{name} 실패:\n{r.stdout}\n{r.stderr}")
    out = "\n".join(l.rstrip() for l in r.stdout.splitlines() if not NOISE.search(l))
    (D / "outs").mkdir(exist_ok=True)
    (D / "outs" / f"{name}.txt").write_text(out, encoding="utf-8")
    t = t.replace(f"<<CODE {name}>>", f"```python\n{src}\n```")
    t = t.replace(f"<<OUT {name}>>", f"```text\n{out}\n```")
    outs[name] = out
    print(f"[{name}] 완료", flush=True)
if only:
    sys.exit(0)
for name in sorted(set(re.findall(r"<<TEXT (\w+)>>", t))):      # 블록 밖에서 직접 실행한 명령의 출력
    t = t.replace(f"<<TEXT {name}>>", f"```text\n{(D / f'{name}.txt').read_text(encoding='utf-8').rstrip()}\n```")
for rel in sorted(set(re.findall(r"<<FILE ([\w./-]+)>>", t))):
    f = D / rel
    lang = "dockerfile" if f.name == "Dockerfile" else LANG.get(f.suffix, "text")
    t = t.replace(f"<<FILE {rel}>>", f"```{lang}\n{f.read_text(encoding='utf-8').rstrip()}\n```")
assert "<<" not in t, re.findall(r"<<[^>]*>>", t)[:5]
dst.write_text(t, encoding="utf-8")
print("blocks:", len(outs))
