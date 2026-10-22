"""examples/volN 의 예제 파일을 모두 실행해 본다.

- 패키지 폴더(__init__.py가 있거나 src/ 아래) 안의 모듈은 import 해 본다.
- 그 밖의 파일은 그 폴더에서 스크립트로 실행한다(키보드 입력은 없음으로).
- 예제가 만드는 파일(txt, json, db, 그림)이 배포 폴더에 남지 않도록 임시 복사본에서 돌린다.
- expected_errors.txt 에 적힌 파일은 실패해도 정상이다(일부러 보여 주는 오류, 키보드 입력, 새 버전 전용).

2권은 장 폴더마다 원고를 만들 때처럼 bNN 파일을 이름순으로 한 폴더에서 차례로 실행한다
(앞 블록이 저장한 모델·데이터를 뒤 블록이 쓰기 때문). 그 밖의 모듈은 문법만 확인하고,
실습 프로젝트(..._service)는 그 폴더에서 본문의 명령(ONNX 내보내기, pytest)을 프로젝트 자신의 uv 환경으로 돌린다.

사용: uv run python tools/check_examples.py --vol 1
      uv run --project examples/vol2 python tools/check_examples.py --vol 2 [--chapters 09 10]
(예제에 필요한 패키지는 examples/volN/pyproject.toml 기준으로 설치된 환경에서 돌린다)
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TIMEOUT = 60
# 2권 독자는 한 폴더에서 모든 장을 실행하므로, 앞 장이 저장한 파일을 뒤 장이 그대로 연다.
# 장마다 폴더를 나눈 예제에서는 그 파일을 앞 장 폴더에서 가져와야 한다 (README에도 같은 표).
# (가져올 장, 파일 이름, 이 장 안에 둘 곳)
CHAPTER_INPUTS = {
    "09": [("06", "fashion_mlp.pt", "fashion_mlp.pt")],
    "19": [("09", "fashion_cnn.pt", "fashion_cnn.pt"), ("09", "fashion_resnet.pt", "fashion_resnet.pt")],
    "20": [("09", "fashion_cnn.pt", "fashion_cnn.pt"), ("09", "fashion_cnn.pt", "fashion_service/models/fashion_cnn.pt")],
}
# 실습 프로젝트는 본문 순서대로, 프로젝트 자신의 환경(uv)에서 실행한다
PROJECT_STEPS = {
    "fashion_service": [["uv", "run", "-q", "--extra", "torch", "python", "-m", "scripts.export_onnx"],
                        ["uv", "run", "-q", "--extra", "torch", "pytest", "-q"]],
    "restaurant_service": [["uv", "run", "-q", "pytest", "-q"]],
}
VOL2_TIMEOUT = 1800  # 2권은 학습 블록이 있어 길게 (원고 기준 블록 하나 수 분)


def is_package_module(path: Path, base: Path) -> bool:
    rel = path.relative_to(base)
    return "src" in rel.parts or (path.parent / "__init__.py").exists()


def module_name(path: Path, project: Path) -> str:
    rel = path.relative_to(project).with_suffix("")
    parts = [p for p in rel.parts if p != "src" and p != "__init__"]
    return ".".join(parts)


def project_root(path: Path, chapter: Path) -> Path:
    """패키지 모듈의 프로젝트 루트: 패키지 폴더(또는 src)의 바로 위 폴더."""
    cur = path.parent
    while cur != chapter and ((cur / "__init__.py").exists() or cur.name == "src"):
        cur = cur.parent
    return cur


def run_one(path: Path, chapter: Path) -> tuple[bool, str]:
    if is_package_module(path, chapter):
        proj = project_root(path, chapter)
        env = dict(os.environ, PYTHONPATH=f"{proj}{os.pathsep}{proj / 'src'}", MPLBACKEND="Agg")
        cmd = [sys.executable, "-c", f"import {module_name(path, proj)}"]
        cwd = proj
    else:
        cwd = path.parent
        env = dict(os.environ, PYTHONPATH=f"{cwd}{os.pathsep}{cwd / 'src'}", MPLBACKEND="Agg")
        cmd = [sys.executable, path.name]
    try:
        r = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True,
                           timeout=TIMEOUT, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return False, "timeout"
    last = (r.stderr.strip().splitlines() or [""])[-1]
    return r.returncode == 0, last


def run_cmd(cmd: list[str], cwd: Path) -> tuple[bool, str, float]:
    env = dict(os.environ, PYTHONPATH=str(cwd), MPLBACKEND="Agg")
    if cmd[0] == "uv":
        env.pop("VIRTUAL_ENV", None)
    start = time.perf_counter()
    try:
        r = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True,
                           timeout=VOL2_TIMEOUT, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return False, "timeout", time.perf_counter() - start
    tail = (r.stderr.strip() or r.stdout.strip()).splitlines()
    return r.returncode == 0, (tail or [""])[-1], time.perf_counter() - start


def check_vol2(base: Path, chapters: list[str]) -> int:
    expected = read_expected(base)
    ok = bad = exp_ok = 0
    for chapter in sorted(p for p in base.iterdir() if p.is_dir() and not p.name.startswith(".")):
        if chapters and not any(chapter.name.startswith(c) for c in chapters):
            continue
        prepare_chapter(base, chapter)
        jobs: list[tuple[str, list[str], Path]] = []
        for f in sorted(chapter.glob("*.py")):
            if f.name.startswith("b"):
                jobs.append((f.name, [sys.executable, "-W", "ignore", f.name], chapter))
            else:
                jobs.append((f.name, [sys.executable, "-m", "py_compile", f.name], chapter))
        for project in sorted(chapter.glob("*_service")):
            for step in PROJECT_STEPS[project.name]:
                jobs.append((f"{project.name}: {' '.join(step[3:])}", step, project))
        for name, cmd, cwd in jobs:
            rel = f"{chapter.name}/{name}"
            passed, err, secs = run_cmd(cmd, cwd)
            if rel in expected and not passed:
                exp_ok += 1
                mark = "~"
            elif passed:
                ok += 1
                mark = "O"
            else:
                bad += 1
                mark = "X"
            print(f"[{mark}] {rel} ({secs:.0f}초){'' if passed else ': ' + err[:200]}", flush=True)
    print(f"\n통과 {ok}개, 의도된 실패 {exp_ok}개, 문제 {bad}개")
    return bad


def prepare_chapter(base: Path, chapter: Path) -> None:
    """앞 장이 만든 파일을 가져오고, BOOK_DATA_DIR가 있으면 data/를 그 폴더로 잇는다."""
    for src_prefix, name, dest in CHAPTER_INPUTS.get(chapter.name[:2], []):
        src = next(base.glob(f"{src_prefix}-*/{name}"), None)
        if src is None:
            print(f"[!] {chapter.name}: {src_prefix}장의 {name}이 없음 — 그 장을 먼저 검사하세요", flush=True)
        else:
            (chapter / dest).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src, chapter / dest)
    data_dir = os.environ.get("BOOK_DATA_DIR")
    if data_dir and not (chapter / "data").exists():
        (chapter / "data").symlink_to(data_dir)     # 원고처럼 data/를 직접 여는 예제(19장 등)를 위해


def read_expected(base: Path) -> set[str]:
    expected_file = base / "expected_errors.txt"
    if not expected_file.exists():
        return set()
    lines = expected_file.read_text(encoding="utf-8").splitlines()
    return {line.split("#")[0].strip() for line in lines} - {""}


def main() -> None:
    parser = argparse.ArgumentParser(description="예제 파일 실행 검사")
    parser.add_argument("--vol", type=int, default=1)
    parser.add_argument("--chapters", nargs="*", default=[], help="2권: 검사할 장 번호 접두어")
    args = parser.parse_args()
    source = ROOT / "examples" / f"vol{args.vol}"
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / source.name
        shutil.copytree(source, base, ignore=shutil.ignore_patterns(".*", "__pycache__"))
        bad = check_vol2(base, args.chapters) if args.vol == 2 else check_all(base)
    sys.exit(1 if bad else 0)


def check_all(base: Path) -> int:
    expected = read_expected(base)
    ok = bad = exp_ok = 0
    for chapter in sorted(p for p in base.iterdir() if p.is_dir() and not p.name.startswith(".")):
        for path in sorted(chapter.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            rel = str(path.relative_to(base))
            passed, err = run_one(path, chapter)
            if rel in expected and not passed:
                exp_ok += 1
            elif passed:
                ok += 1
            else:
                bad += 1
                print(f"[X] {rel}: {err[:150]}")
    print(f"\n통과 {ok}개, 의도된 오류 {exp_ok}개, 문제 {bad}개")
    return bad


if __name__ == "__main__":
    main()
