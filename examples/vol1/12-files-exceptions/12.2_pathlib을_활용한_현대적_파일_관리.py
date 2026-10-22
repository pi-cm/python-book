"""1권 Chapter 12: 파일과 예외 처리 — 12.2 pathlib을 활용한 현대적 파일 관리

원고: manuscript/chapters/12-files-exceptions.md (358줄부터)
"""

# ---- 원고 358줄 ----
from pathlib import Path
import os
import shutil
from datetime import datetime

def pathlib_basics():
    """pathlib 기본 사용법"""
    
    # 경로 생성 (운영체제 독립적)
    current_dir = Path.cwd()  # 현재 작업 디렉터리
    home_dir = Path.home()   # 홈 디렉터리
    
    print(f"현재 디렉터리: {current_dir}")
    print(f"홈 디렉터리: {home_dir}")
    
    # 경로 조합 (/ 연산자 사용)
    data_dir = current_dir / "data" / "korean_files"
    config_file = current_dir / "config" / "settings.json"
    
    print(f"데이터 디렉터리: {data_dir}")
    print(f"설정 파일: {config_file}")
    
    # 경로 정보 추출
    sample_path = Path("/Users/username/Documents/projects/python_book/chapter01.md")
    
    print(f"\n경로 정보 추출:")
    print(f"전체 경로: {sample_path}")
    print(f"파일명: {sample_path.name}")
    print(f"확장자: {sample_path.suffix}")
    print(f"확장자 제외 이름: {sample_path.stem}")
    print(f"부모 디렉터리: {sample_path.parent}")
    print(f"모든 부모: {list(sample_path.parents)}")
    print(f"루트: {sample_path.anchor}")
    print(f"경로 부분들: {sample_path.parts}")
    
    # 절대경로와 상대경로
    relative_path = Path("docs/korean/tutorial.md")
    absolute_path = relative_path.resolve()
    
    print(f"\n경로 변환:")
    print(f"상대 경로: {relative_path}")
    print(f"절대 경로: {absolute_path}")
    print(f"상대 경로 여부: {relative_path.is_absolute()}")
    print(f"절대 경로 여부: {absolute_path.is_absolute()}")

def pathlib_file_operations():
    """pathlib을 이용한 파일 작업"""
    
    # 작업 디렉터리 생성
    work_dir = Path("pathlib_demo")
    work_dir.mkdir(exist_ok=True)
    
    # 중첩 디렉터리 생성
    korean_dir = work_dir / "korean_docs" / "tutorials" 
    korean_dir.mkdir(parents=True, exist_ok=True)
    
    # 파일 생성 및 쓰기
    tutorial_file = korean_dir / "파이썬_기초.md"
    tutorial_content = """# 파이썬 기초 튜토리얼

## 1. 소개
파이썬은 배우기 쉽고 강력한 프로그래밍 언어입니다.

## 2. 변수와 데이터 타입
- 정수형: int
- 실수형: float  
- 문자열: str
- 불린형: bool

## 3. 한글 처리
파이썬은 유니코드를 지원하므로 한글 처리가 용이합니다.
"""
    
    tutorial_file.write_text(tutorial_content, encoding="utf-8")
    
    # 파일 정보 확인
    print(f"파일 생성: {tutorial_file}")
    print(f"파일 존재: {tutorial_file.exists()}")
    print(f"파일 여부: {tutorial_file.is_file()}")
    print(f"디렉터리 여부: {tutorial_file.is_dir()}")
    print(f"파일 크기: {tutorial_file.stat().st_size} bytes")
    
    # 파일 시간 정보
    stat = tutorial_file.stat()
    changed_time = datetime.fromtimestamp(stat.st_ctime)  # 맥·리눅스: 상태 변경 시각, 윈도우: 생성 시각
    modified_time = datetime.fromtimestamp(stat.st_mtime)
    
    print(f"상태 변경 시간(st_ctime): {changed_time}")
    print(f"수정 시간: {modified_time}")
    
    # 파일 읽기
    content = tutorial_file.read_text(encoding="utf-8")
    print(f"\n파일 내용 (첫 100자):")
    print(content[:100] + "...")
    
    # 파일 복사
    backup_file = korean_dir / "파이썬_기초_백업.md"
    backup_file.write_text(content, encoding="utf-8")
    
    # 파일명 변경
    new_name = korean_dir / "Python_기초_한글.md"
    tutorial_file.rename(new_name)
    
    print(f"파일명 변경: {tutorial_file} → {new_name}")
    
    # 디렉터리 내용 탐색
    print(f"\n{korean_dir} 디렉터리 내용:")
    for item in korean_dir.iterdir():
        if item.is_file():
            print(f"{item.name} ({item.stat().st_size} bytes)")
        elif item.is_dir():
            print(f"{item.name}/")
    
    # 패턴 매칭으로 파일 찾기
    print(f"\n마크다운 파일 찾기:")
    for md_file in korean_dir.glob("*.md"):
        print(f"  {md_file.name}")
    
    # 재귀적 검색
    print(f"\n모든 마크다운 파일 (재귀 검색):")
    for md_file in work_dir.rglob("*.md"):
        relative_path = md_file.relative_to(work_dir)
        print(f"  {relative_path}")
    
    # 정리
    shutil.rmtree(work_dir)
    print(f"\n정리: {work_dir} 디렉터리 삭제")

def advanced_pathlib():
    """pathlib 고급 활용"""
    
    # 프로젝트 구조 생성
    project_root = Path("korean_project")
    
    # 전형적인 파이썬 프로젝트 구조
    directories = [
        "src/korean_app",
        "tests/unit", 
        "tests/integration",
        "docs/api",
        "docs/tutorials",
        "data/raw",
        "data/processed",
        "config",
        "logs"
    ]
    
    for dir_path in directories:
        (project_root / dir_path).mkdir(parents=True, exist_ok=True)
    
    # 파일 생성
    files_to_create = {
        "README.md": "# 한국어 프로젝트\n\n파이썬으로 만든 한국어 처리 애플리케이션",
        "requirements.txt": "requests>=2.28.0\npandas>=1.5.0\nfastapi>=0.85.0",
        "src/korean_app/__init__.py": "# 한국어 앱 패키지",
        "src/korean_app/main.py": 'def main():\n    print("안녕하세요, 한국어 앱입니다!")',
        "config/settings.json": '{\n  "language": "ko",\n  "debug": true\n}',
        "data/raw/sample.txt": "안녕하세요\n한글 데이터 샘플입니다"
    }
    
    for file_path, content in files_to_create.items():
        full_path = project_root / file_path
        full_path.write_text(content, encoding="utf-8")
    
    print(f"프로젝트 구조 생성 완료: {project_root}")
    
    # 프로젝트 분석
    def analyze_project(root_path: Path):
        """프로젝트 구조 분석"""
        total_files = 0
        total_size = 0
        file_types = {}
        
        for file_path in root_path.rglob("*"):
            if file_path.is_file():
                total_files += 1
                file_size = file_path.stat().st_size
                total_size += file_size
                
                extension = file_path.suffix.lower() or "확장자없음"
                if extension not in file_types:
                    file_types[extension] = {"count": 0, "size": 0}
                
                file_types[extension]["count"] += 1
                file_types[extension]["size"] += file_size
        
        return {
            "총파일수": total_files,
            "총크기": total_size,
            "파일타입별": file_types
        }
    
    analysis = analyze_project(project_root)
    
    print(f"\n프로젝트 분석 결과:")
    print(f"총 파일 수: {analysis['총파일수']}")
    print(f"총 크기: {analysis['총크기']} bytes")
    print(f"파일 타입별 통계:")
    
    for ext, info in analysis["파일타입별"].items():
        print(f"  {ext}: {info['count']}개 파일, {info['size']} bytes")
    
    # 특정 파일 찾기
    print(f"\n파이썬 파일 찾기:")
    python_files = list(project_root.rglob("*.py"))
    for py_file in python_files:
        rel_path = py_file.relative_to(project_root)
        size = py_file.stat().st_size
        print(f"  {rel_path} ({size} bytes)")
    
    # 빈 디렉터리 찾기
    print(f"\n빈 디렉터리:")
    for dir_path in project_root.rglob("*"):
        if dir_path.is_dir() and not any(dir_path.iterdir()):
            rel_path = dir_path.relative_to(project_root)
            print(f"  {rel_path}/")
    
    # 정리
    shutil.rmtree(project_root)
    print(f"\n정리: {project_root} 프로젝트 삭제")

# 실행
print("=== pathlib 기본 사용법 ===")
pathlib_basics()

print("\n=== pathlib 파일 작업 ===")
pathlib_file_operations()

print("\n=== pathlib 고급 활용 ===")
advanced_pathlib()
