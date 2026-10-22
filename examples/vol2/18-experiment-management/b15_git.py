# [2권 Chapter 18. 실험 관리와 재현성 · 18.7 데이터·코드·환경 버전 기록 · manuscript-vol2/chapters/18-experiment-management.md:1154]
import os
import subprocess
import tempfile
from pathlib import Path


def 코드_버전(폴더: Path) -> dict:
    """git 커밋 번호와, 커밋하지 않은 수정이 남아 있는지를 알려 준다."""
    def git(*명령) -> str:
        return subprocess.run(["git", *명령], cwd=폴더, capture_output=True, text=True,
                              check=True).stdout.strip()
    try:
        커밋 = git("rev-parse", "HEAD")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {"커밋": None, "수정됨": None}         # git 저장소가 아니거나 git이 없음
    바뀐_파일 = git("status", "--porcelain")          # 커밋 안 한 변경이 있으면 한 줄 이상
    return {"커밋": 커밋[:12], "수정됨": bool(바뀐_파일)}


# 연습용 저장소를 임시 폴더에 만들어 본다 (날짜·시간대·이름을 고정해 커밋 번호가 늘 같게)
고정 = {"GIT_AUTHOR_NAME": "책", "GIT_AUTHOR_EMAIL": "book@example.com",
        "GIT_AUTHOR_DATE": "2026-01-01T00:00:00+09:00", "GIT_COMMITTER_NAME": "책",
        "GIT_COMMITTER_EMAIL": "book@example.com", "GIT_COMMITTER_DATE": "2026-01-01T00:00:00+09:00"}
os.environ.update(고정)
with tempfile.TemporaryDirectory() as 임시:
    폴더 = Path(임시)
    print("git 저장소가 아닐 때:", 코드_버전(폴더))
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=폴더, check=True)
    (폴더 / "학습.py").write_text("학습률 = 0.001\n", encoding="utf-8")
    subprocess.run(["git", "add", "학습.py"], cwd=폴더, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "첫 실험 코드"], cwd=폴더, check=True)
    print("커밋한 직후        :", 코드_버전(폴더))
    (폴더 / "학습.py").write_text("학습률 = 0.003\n", encoding="utf-8")   # 커밋 없이 고침
    print("커밋 없이 고친 뒤  :", 코드_버전(폴더))
