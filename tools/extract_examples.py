"""원고(마크다운)에서 파이썬 예제를 뽑아 독자 배포용 파일로 만든다.

원고가 원본이다. 원고를 고치면 이 스크립트를 다시 돌려 예제를 새로 만든다.

규칙
- 첫 줄이 `# 경로.py` 인 블록은 그 경로의 파일로 만든다(다중 파일 프로젝트).
  같은 경로가 앞 절에서 이미 나왔으면, 그 절의 경로 파일들을 모두 절 이름 폴더로 따로 모은다.
- 나머지 블록은 절(##)마다 하나의 파일로 모은다. 같은 절의 블록은 차례대로 이어 붙인다
  (원고에서 앞 블록의 정의를 이어 쓰는 경우가 많기 때문).
- 절을 넘어 앞 절의 정의를 이어 쓰는 장(CUMULATIVE)은 본문 설계대로 한 파일로 묶는다.
- 따로 떼는 블록: 일부러 오류를 보여 주는 블록(마지막 줄 주석에 오류 이름이 있거나 부록 D),
  input()으로 입력을 받는 블록, 특정 파이썬 버전 이상에서만 도는 블록.
  이 블록들은 expected_errors.txt에 이유와 함께 적는다(실패가 정상).
- 파일마다 첫 줄에 권·장·절과 원고 위치를 적는다.

2권은 원고를 만들 때 코드 블록마다 따로 실행한 파일(build-src/vol2)이 있고, 원고의 블록은 그 파일과
글자 하나까지 같다. 그래서 2권은 블록마다 그 파일 이름 그대로 뽑는다(서로 import하는 이름이 살아 있도록).
build-src에 짝이 없는 블록은 실행용이 아닌 짧은 조각이라 뽑지 않는다.
다른 장에서 만든 모듈을 불러 쓰면 그 모듈을 장 폴더에 함께 복사한다.

사용: uv run python tools/extract_examples.py --vol 1
"""

import argparse
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VOLUMES = {
    1: (ROOT / "manuscript", ROOT / "examples" / "vol1"),
    2: (ROOT / "manuscript-vol2", ROOT / "examples" / "vol2"),
}
PATH_HEADER = re.compile(r"^#\s*([\w./-]+\.py)\b")
ERROR_COMMENT = re.compile(r"#\s*\w*(Error|Exception)\b")
VERSION_HEADER = re.compile(r"^#\s*Python\s+3\.(\d+)\s*이상")
BASE_MINOR = 12  # 예제 기준 파이썬 3.12 (examples/volN/pyproject.toml의 requires-python)
# 절을 넘어 앞 절의 정의를 이어 쓰는 장: {원고 파일 이름: 한 파일로 묶을 절 번호 접두어(빈 튜플이면 장 전체)}
CUMULATIVE = {
    "13-inheritance-polymorphism.md": ("13.1", "13.2", "13.3", "13.4"),
    "18-database-integration.md": (),
    "20-data-analysis-visualization.md": (),
}
# 장마다 오류 시연으로 보는 원고 (블록마다 따로 떼어 실패를 정상으로 둔다)
ERROR_DEMO_FILES = {"D-troubleshooting.md"}
# 읽기만 하는 참고용 파일 (본문이 실행하지 말고 읽어 보라고 소개한다)
READ_ONLY_FILES = {"setup.py": "참고용 레거시 예제(읽기만 하고 실행하지 않음)"}
SECTION_NUMBER = re.compile(r"^(\d+\.\d+)\s+")
UNSAFE = re.compile(r"[^\w가-힣.-]+")
MAX_SLUG = 40


@dataclass
class Block:
    line: int
    code: str


@dataclass
class Section:
    title: str
    blocks: list[Block] = field(default_factory=list)


def parse(md: Path) -> list[Section]:
    """마크다운을 절(##) 단위로 나누고 python 블록을 모은다."""
    sections = [Section("들어가며")]
    lines = md.read_text(encoding="utf-8").splitlines()
    in_code, lang, buf, start = False, "", [], 0
    for i, line in enumerate(lines, 1):
        if line.startswith("```"):
            if not in_code:
                in_code, lang, buf, start = True, line[3:].strip(), [], i
            else:
                in_code = False
                if lang == "python":
                    sections[-1].blocks.append(Block(start, "\n".join(buf)))
            continue
        if in_code:
            buf.append(line)
        elif line.startswith("## "):
            sections.append(Section(line[3:].strip()))
    return [s for s in sections if s.blocks]


def slug(title: str) -> str:
    title = re.sub(r"[`*()\[\]:,'\"]", "", title)
    return UNSAFE.sub("_", title).strip("_")[:MAX_SLUG].rstrip("_")


def chapter_label(md: Path, vol: int) -> str:
    first = md.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip()
    return f"{vol}권 {first}"


def classify(block: Block, md_name: str) -> str | None:
    """따로 떼어 실패를 정상으로 둘 블록이면 그 이유를 돌려준다."""
    lines = [line for line in block.code.splitlines() if line.strip()]
    first, last = (lines[0], lines[-1]) if lines else ("", "")
    m = VERSION_HEADER.match(first.strip())
    if m and int(m.group(1)) > BASE_MINOR:
        return f"Python 3.{m.group(1)} 이상에서만 실행됨"
    if md_name in ERROR_DEMO_FILES or ERROR_COMMENT.search(last):
        return "일부러 오류를 보여 주는 예제"
    if "input(" in block.code:
        return "키보드 입력이 필요한 예제(직접 실행해 입력)"
    return None


def ensure_package_inits(out_dir: Path, created: list[Path]) -> None:
    """src/ 아래 패키지 폴더에 __init__.py가 없으면 빈 파일로 둔다(원고에 내용이 없는 하위 패키지)."""
    for f in created:
        for parent in f.relative_to(out_dir).parents:
            if "src" not in parent.parts or parent.name == "src":
                continue
            init = out_dir / parent / "__init__.py"
            if not init.exists():
                init.write_text('"""원고에 내용이 없는 패키지 표시용 빈 파일."""\n', encoding="utf-8")


def write_plain(path: Path, label: str, title: str, rel_md: Path, blocks: list[Block]) -> None:
    parts = [f'"""{label} — {title}\n\n원고: {rel_md} ({blocks[0].line}줄부터)\n"""\n']
    for b in blocks:
        parts.append(f"# ---- 원고 {b.line}줄 ----\n{b.code}\n")
    path.write_text("\n".join(parts), encoding="utf-8")


def extract_chapter(md: Path, out_dir: Path, vol: int, expected: list[str], base: Path) -> int:
    label = chapter_label(md, vol)
    rel_md = md.relative_to(ROOT)
    written = 0
    seen_paths: set[str] = set()
    created: list[Path] = []
    cumulative = CUMULATIVE.get(md.name)
    merged: list[Block] = []
    merged_titles: list[str] = []
    for order, sec in enumerate(parse(md), 1):
        m = SECTION_NUMBER.match(sec.title)
        sec_no = m.group(1) if m else ""
        sec_name = f"{sec_no}_{slug(sec.title[m.end():])}" if m else f"{order:02d}_{slug(sec.title)}"
        path_blocks = [(b, PATH_HEADER.match(b.code.strip())) for b in sec.blocks]
        file_blocks = [(b, mm.group(1)) for b, mm in path_blocks if mm]
        plain = [b for b, mm in path_blocks if not mm]

        # 경로 파일: 앞 절과 이름이 겹치면 이 절의 경로 파일을 절 폴더로 모은다
        collide = any(p in seen_paths for _, p in file_blocks)
        target_base = out_dir / sec_name if collide else out_dir
        for b, p in file_blocks:
            target = target_base / p
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f"# [{label} · {sec.title} · {rel_md}:{b.line}]\n" + b.code + "\n", encoding="utf-8")
            seen_paths.add(p)
            created.append(target)
            written += 1
            reason = READ_ONLY_FILES.get(p) or classify(b, md.name)
            if reason:
                expected.append(f"{target.relative_to(base)}  # {reason}")

        # 따로 떼는 블록과 이어 붙일 블록 나누기
        keep: list[Block] = []
        for n, b in enumerate(plain, 1):
            reason = classify(b, md.name)
            if reason:
                f = out_dir / f"{sec_name}_따로_{n}.py"
                write_plain(f, label, sec.title, rel_md, [b])
                expected.append(f"{f.relative_to(base)}  # {reason}")
                written += 1
            else:
                keep.append(b)
        if not keep:
            continue
        in_cumulative = cumulative is not None and (cumulative == () or sec_no in cumulative)
        if in_cumulative:
            merged.extend(keep)
            merged_titles.append(sec.title)
        else:
            write_plain(out_dir / f"{sec_name}.py", label, sec.title, rel_md, keep)
            written += 1

    if merged:
        first = SECTION_NUMBER.match(merged_titles[0])
        last = SECTION_NUMBER.match(merged_titles[-1])
        span = f"{first.group(1)}-{last.group(1)}" if first and last else "전체"
        title = f"{merged_titles[0]} ~ {merged_titles[-1]} (앞 절의 정의를 이어 쓰므로 한 파일로 묶음)"
        write_plain(out_dir / f"{span}_이어서_실행.py", label, title, rel_md, merged)
        written += 1
    ensure_package_inits(out_dir, created)
    apply_reader_steps(md.name, out_dir)
    return written


def apply_reader_steps(md_name: str, out_dir: Path) -> None:
    """본문이 독자에게 시키는 준비 작업을 그대로 해 둔다."""
    if md_name == "14-modules-packages.md":
        # 14.8절: 앞 절의 models 폴더와 search.py를 새 프로젝트로 복사하고 import 한 줄 고치기
        src_pkg = out_dir / "seoul_restaurants"
        dst_pkg = out_dir / "src" / "seoul_restaurant_finder"
        if src_pkg.exists() and dst_pkg.exists():
            shutil.copytree(src_pkg / "models", dst_pkg / "models", dirs_exist_ok=True)
            search = (src_pkg / "services" / "search.py").read_text(encoding="utf-8")
            (dst_pkg / "search.py").write_text(
                search.replace("from ..models import Restaurant", "from .models import Restaurant"), encoding="utf-8")


BUILD_SRC = ROOT / "build-src" / "vol2"
PROJECT_SUFFIX = "_service"
PROJECT_IGNORE = shutil.ignore_patterns("__pycache__", ".pytest_cache", ".venv", "*.onnx", "*.pt", "*.data")
LOCAL_IMPORT = re.compile(r"^\s*(?:from|import)\s+([가-힣][\w가-힣]*)", re.M)


def build_src_dir(md: Path) -> Path:
    """원고 파일에 짝이 되는 생성 소스 폴더 (장은 v2cNN, 부록은 v2app/A 등)."""
    head = md.name[:2]
    return BUILD_SRC / (f"v2c{head}" if head.isdigit() else f"v2app/{md.name[0]}")


def source_files(src: Path) -> dict[str, Path]:
    """생성 소스의 파이썬 파일을 내용으로 찾을 수 있게 모은다.

    같은 내용이면 위쪽 폴더의 파일을, 그중에서도 블록 이름(bNN_)보다 모듈 이름을 쓴다.
    모듈을 보여 주는 블록은 다른 블록이 그 모듈 이름으로 import하기 때문이다.
    """
    found: dict[str, Path] = {}
    for f in sorted(src.rglob("*.py"), key=lambda f: (len(f.parts), bool(re.match(r"b\d", f.name)), f.name)):
        if "__pycache__" in f.parts or f.name.startswith("fill"):
            continue
        found.setdefault(f.read_text(encoding="utf-8").strip(), f)
    return found


def extract_chapter_vol2(md: Path, out_dir: Path, skipped: list[str]) -> int:
    label = chapter_label(md, 2)
    rel_md = md.relative_to(ROOT)
    src = build_src_dir(md)
    sources = source_files(src)
    written = 0
    for sec in parse(md):
        for b in sec.blocks:
            match = sources.get(b.code.strip())
            if match is None:
                skipped.append(f"{rel_md}:{b.line}")
                continue
            rel = match.relative_to(src)
            if rel.parts[0].endswith(PROJECT_SUFFIX):
                # 실습 프로젝트(..._service)는 폴더 구조와 Dockerfile·pyproject까지 통째로 둔다
                project = out_dir / rel.parts[0]
                if not project.exists():
                    shutil.copytree(src / rel.parts[0], project, ignore=PROJECT_IGNORE)
                target = out_dir / rel
            else:
                target = out_dir / match.name
            target.write_text(f"# [{label} · {sec.title} · {rel_md}:{b.line}]\n" + b.code.rstrip("\n") + "\n",
                              encoding="utf-8")
            written += 1
    return written


def copy_shared_modules(dst: Path) -> list[str]:
    """다른 장에서 만든 모듈을 import하는 장 폴더에 그 모듈을 복사한다."""
    owners: dict[str, Path] = {}
    for f in sorted(dst.glob("*/*.py")):
        if not re.match(r"b\d", f.name):
            owners.setdefault(f.stem, f)
    copied = []
    for chapter in sorted(p for p in dst.iterdir() if p.is_dir() and not p.name.startswith(".")):
        pending = list(chapter.glob("*.py"))
        while pending:
            f = pending.pop()
            for name in LOCAL_IMPORT.findall(f.read_text(encoding="utf-8")):
                target = chapter / f"{name}.py"
                if not target.exists() and name in owners:
                    shutil.copy(owners[name], target)
                    copied.append(f"{target.relative_to(dst)} ← {owners[name].relative_to(dst)}")
                    pending.append(target)
    return copied


# NVIDIA GPU가 없는 컴퓨터(맥, CPU)에서 실패하는 것이 정상인 2권 예제. 4090 서버(GPU 2장)에서는 모두 통과했다.
VOL2_GPU_ONLY = {
    "16-gpu-performance": ("NVIDIA GPU가 있어야 실행됨", [
        "b01_환경", "b02_병렬", "b03_잘못재기", "b04_재기도구", "b05_교차점", "b06_메모리", "b07_활성화메모리",
        "b08_OOM", "b09_고정메모리", "b12_GradScaler", "b13_정밀도비교", "b14_TF32", "b15_compile",
        "b16_융합", "b17_compile모드", "b19_SDPA", "b20_프로파일러", "b21_병목찾기", "b22_배치처리량", "b23_실습"]),
    "17-distributed-training": ("NVIDIA GPU(대부분 2장)와 torchrun으로 실행 — 본문의 실행 명령 참고", [
        "b01_메모리_내역", "b04_누적_메모리", "b05_체크포인팅", "b06_첫_allreduce", "b07_통신_비용",
        "b08_ddp_옷분류", "b09_ddp_같은가", "b10_처리량", "b11_no_sync", "b12_fsdp", "b15_멈춤"]),
}


def write_vol2_expected(dst: Path) -> int:
    lines = ["# GPU가 없는 컴퓨터에서 실패하는 것이 정상인 예제 (tools/extract_examples.py가 만듦)",
             "# 모두 RTX 4090 두 장이 달린 리눅스 서버에서 본문의 실행 방법대로 통과했다."]
    for chapter, (reason, names) in VOL2_GPU_ONLY.items():
        for name in names:
            assert (dst / chapter / f"{name}.py").exists(), name
            lines.append(f"{chapter}/{name}.py  # {reason}")
    (dst / "expected_errors.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(lines) - 2


def main_vol2(src: Path, dst: Path) -> None:
    total = 0
    skipped: list[str] = []
    for folder in ("chapters", "appendix"):
        for md in sorted((src / folder).glob("*.md")):
            out_dir = dst / (md.stem if folder == "chapters" else f"{folder}-{md.stem}")
            out_dir.mkdir(parents=True, exist_ok=True)
            n = extract_chapter_vol2(md, out_dir, skipped)
            if n == 0:
                out_dir.rmdir()
            total += n
    copied = copy_shared_modules(dst)
    gpu_only = write_vol2_expected(dst)
    print(f"2권 예제 파일 {total}개 → {dst.relative_to(ROOT)}, 다른 장 모듈 복사 {len(copied)}개, "
          f"GPU 전용 {gpu_only}개")
    print("뽑지 않은 조각:", ", ".join(skipped))


def main() -> None:
    parser = argparse.ArgumentParser(description="원고에서 예제 파일 뽑기")
    parser.add_argument("--vol", type=int, choices=sorted(VOLUMES), default=1)
    args = parser.parse_args()
    src, dst = VOLUMES[args.vol]
    # 손으로 관리하는 파일(pyproject.toml, README.md, uv.lock, .venv)은 남기고 생성물 폴더만 지운다
    if dst.exists():
        for old in dst.iterdir():
            if old.is_dir() and not old.name.startswith("."):
                shutil.rmtree(old)
    if args.vol == 2:
        main_vol2(src, dst)
        return
    total = 0
    expected: list[str] = []
    for folder in ("chapters", "references", "appendix"):
        for md in sorted((src / folder).glob("*.md")):
            out_dir = dst / (md.stem if folder == "chapters" else f"{folder}-{md.stem}")
            out_dir.mkdir(parents=True, exist_ok=True)
            n = extract_chapter(md, out_dir, args.vol, expected, dst)
            if n == 0:
                out_dir.rmdir()
            total += n
    header = "# 실행하면 실패하는 것이 정상인 예제와 그 이유 (tools/extract_examples.py가 만듦)\n"
    (dst / "expected_errors.txt").write_text(header + "\n".join(expected) + "\n", encoding="utf-8")
    print(f"{args.vol}권 예제 파일 {total}개 → {dst.relative_to(ROOT)} (실패가 정상인 예제 {len(expected)}개)")


if __name__ == "__main__":
    main()
