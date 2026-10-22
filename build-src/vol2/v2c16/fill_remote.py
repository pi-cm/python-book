"""template.md의 <<CODE x>>/<<OUT x>>를 코드 파일과, 원격 GPU에서 실행해 받아 둔 출력(outs/x.txt)으로 채운다.

16·17장은 이 Mac이 아니라 4090 서버(cq 워커)에서 실행한다. 출력은 실행 결과를 outs/에 그대로 저장해 두고,
이 스크립트는 실행 없이 채우기만 한다. 코드 파일이 출력보다 새것이면(실행 뒤 코드를 고쳤으면) 멈춘다.
사용: python3 fill_remote.py <작업 폴더> <원고 경로>
"""
import re
import sys
from pathlib import Path

D = Path(sys.argv[1]); dst = Path(sys.argv[2])
t = (D / "template.md").read_text(encoding="utf-8")
names = sorted(set(re.findall(r"<<(?:CODE|OUT) (\w+)>>", t)))
problems = []
for name in names:
    code = D / f"{name}.py"
    if not code.exists():
        code = D / f"{name}.sh"
    src = code.read_text(encoding="utf-8").rstrip("\n")
    lang = "bash" if code.suffix == ".sh" else "python"
    t = t.replace(f"<<CODE {name}>>", f"```{lang}\n{src}\n```")
    if f"<<OUT {name}>>" in t:
        out_file = D / "outs" / f"{name}.txt"
        if not out_file.exists():
            problems.append(f"{name}: outs/{name}.txt 없음")
            continue
        if code.stat().st_mtime > out_file.stat().st_mtime:
            problems.append(f"{name}: 코드가 출력보다 새것 — 다시 실행해서 출력을 갱신할 것")
        out = out_file.read_text(encoding="utf-8").rstrip("\n")
        t = t.replace(f"<<OUT {name}>>", f"```text\n{out}\n```")
if problems:
    sys.exit("채우기 실패:\n" + "\n".join(problems))
assert "<<" not in t, "남은 자리표시가 있음"
dst.write_text(t, encoding="utf-8")
print("blocks:", len(names))
