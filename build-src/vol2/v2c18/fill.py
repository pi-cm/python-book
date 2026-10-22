"""template.md의 <<CODE x>>/<<OUT x>>를 실제 코드와 실행 출력으로 채운다 (18장용: 실험 기록 도구 추가, run 폴더에서 실행)."""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

D = Path(sys.argv[1]); dst = Path(sys.argv[2])
RUN = D / "run"                                   # data -> scratchpad/data 링크가 있는 실행 폴더
NOISE = re.compile(r"conversion_method_template|^\s*cpu = ")
env = dict(os.environ, HF_HOME=str(D.parent / "hf"), MLFLOW_DISABLE_AGENT_HINT="1")
t = (D / "template.md").read_text(encoding="utf-8")
outs = {}
only = set(sys.argv[3:])                          # 이름을 주면 그 블록만 실행해 보기
if not only:                                      # 전체 실행이면 앞선 실행의 기록 파일을 지우고 시작
    for p in RUN.iterdir():
        if p.name == "data":
            continue
        shutil.rmtree(p) if p.is_dir() else p.unlink()
for name in sorted(set(re.findall(r"<<(?:CODE|OUT) (\w+)>>", t))):
    if only and name not in only:
        continue
    src = (D / f"{name}.py").read_text(encoding="utf-8").rstrip("\n")
    if name.startswith("b"):
        r = subprocess.run(["uv", "run", "-q", "--no-project", "--python", "3.12", "--with", "torch", "--with", "numpy",
                            "--with", "torchvision", "--with", "scikit-learn", "--with", "tensorboard",
                            "--with", "mlflow", "--with", "optuna", "--with", "pyyaml",
                            "python", "-W", "ignore", str(D / f"{name}.py")],
                           capture_output=True, text=True, cwd=str(RUN), env=env)
        if r.returncode != 0:
            sys.exit(f"{name} 실패:\n{r.stderr}")
        out = "\n".join(l for l in r.stdout.splitlines() if not NOISE.search(l))
    else:
        out = ""                                  # 모듈 파일(실험도구 등)은 코드만 싣는다
    (D / "outs").mkdir(exist_ok=True)
    (D / "outs" / f"{name}.txt").write_text(out, encoding="utf-8")
    print(f"[{name}] 완료", flush=True)
    t = t.replace(f"<<CODE {name}>>", f"```python\n{src}\n```")
    t = t.replace(f"<<OUT {name}>>", f"```text\n{out}\n```")
    outs[name] = out
if only:
    sys.exit(0)
assert not re.search(r"<<(?:CODE|OUT) ", t)
dst.write_text(t, encoding="utf-8")
print("blocks:", len(outs))
