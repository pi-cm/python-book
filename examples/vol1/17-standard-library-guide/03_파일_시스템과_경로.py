"""1권 Chapter 17: 표준 라이브러리 핵심 가이드 — 파일 시스템과 경로

원고: manuscript/chapters/17-standard-library-guide.md (265줄부터)
"""

# ---- 원고 265줄 ----
from pathlib import Path
import os

# 한국어 파일명과 경로
korean_files = Path("데이터") / "한국어" / "고객_정보.txt"
print(f"전체 경로: {korean_files}")
print(f"부모 디렉토리: {korean_files.parent}")
print(f"파일명: {korean_files.name}")
print(f"확장자: {korean_files.suffix}")

# 경로 생성 및 파일 작업
data_dir = Path("한국_프로젝트/데이터")
data_dir.mkdir(parents=True, exist_ok=True)

# 한글 파일 생성 및 처리
korean_file = data_dir / "고객_목록.txt"
customers = ["김철수", "이영희", "박민수", "정수진"]

korean_file.write_text("\n".join(customers), encoding='utf-8')
print(f"파일 크기: {korean_file.stat().st_size} 바이트")

# 파일 읽기
content = korean_file.read_text(encoding='utf-8')
print(f"파일 내용:\n{content}")

# glob 패턴으로 파일 찾기  
for txt_file in data_dir.glob("*.txt"):
    print(f"찾은 파일: {txt_file.name}")

# ---- 원고 304줄 ----
import os
import shutil
from pathlib import Path

# 환경변수 설정
os.environ['한국어_설정'] = '서울_KR'
korean_setting = os.environ.get('한국어_설정', '기본값')
print(f"한국어 설정: {korean_setting}")

# 디렉토리 작업
work_dir = "한국_작업공간"
if not os.path.exists(work_dir):
    os.makedirs(work_dir)

# 파일 복사 및 이동
source = "한국_프로젝트/데이터/고객_목록.txt"
backup = "한국_프로젝트/데이터/백업_고객_목록.txt"

if Path(source).exists():
    shutil.copy2(source, backup)
    print(f"{source} → {backup} 복사 완료")

# 디렉토리 전체 복사
if os.path.exists("한국_프로젝트"):
    shutil.copytree("한국_프로젝트", "한국_프로젝트_백업", dirs_exist_ok=True)
