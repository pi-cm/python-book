# [1권 Chapter 14: 모듈과 패키지 · 14.9 파이썬 내장 모듈 활용 · manuscript/chapters/14-modules-packages.md:1555]
# pathlib_example.py
"""pathlib를 사용한 현대적인 경로 처리"""

from pathlib import Path
import json
from datetime import datetime

# 프로젝트 구조 생성
def setup_restaurant_project():
    """맛집 프로젝트 디렉토리 구조 생성"""
    
    # 기본 디렉토리 구조
    project_root = Path("restaurant_project")
    directories = [
        project_root / "data",
        project_root / "logs",
        project_root / "config",
        project_root / "reports"
    ]
    
    # 디렉토리 생성
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"디렉토리 생성: {directory}")
    
    # 설정 파일 생성
    config_data = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "seoul_restaurants"
        },
        "api": {
            "rate_limit": 1000,
            "timeout": 30
        },
        "search": {
            "max_results": 50,
            "default_radius": 2.0
        }
    }
    
    config_file = project_root / "config" / "settings.json"
    config_file.write_text(
        json.dumps(config_data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"설정 파일 생성: {config_file}")
    
    # 로그 파일 생성
    log_file = project_root / "logs" / f"app_{datetime.now():%Y%m%d}.log"
    log_file.write_text(
        f"[{datetime.now():%Y-%m-%d %H:%M:%S}] 애플리케이션 시작\n",
        encoding="utf-8"
    )
    print(f"로그 파일 생성: {log_file}")
    
    return project_root

# 파일 시스템 탐색
def explore_project(project_root: Path):
    """프로젝트 구조 탐색"""
    print(f"\n=== {project_root.name} 프로젝트 구조 ===")
    
    # 재귀적으로 모든 파일과 디렉토리 탐색
    for path in sorted(project_root.rglob("*")):
        level = len(path.relative_to(project_root).parts)
        indent = "  " * (level - 1)
        
        if path.is_dir():
            print(f"{indent}{path.name}/")
        else:
            size = path.stat().st_size
            print(f"{indent}{path.name} ({size} bytes)")

# 파일 조작 예제
def file_operations_example():
    """pathlib를 사용한 파일 조작"""
    
    # 임시 데이터 디렉토리
    data_dir = Path("temp_data")
    data_dir.mkdir(exist_ok=True)
    
    # 여러 파일 생성
    sample_files = [
        ("restaurants.json", {"count": 150, "last_updated": "2024-01-15"}),
        ("reviews.json", {"total_reviews": 2847, "avg_rating": 4.2}),
        ("districts.json", {"서울시": 25, "경기도": 31})
    ]
    
    created_files = []
    for filename, data in sample_files:
        file_path = data_dir / filename
        file_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        created_files.append(file_path)
        print(f"파일 생성: {file_path}")
    
    print(f"\n총 {len(created_files)}개 파일 생성됨")
    
    # 파일 정보 조회
    for file_path in created_files:
        stat = file_path.stat()
        print(f"\n파일: {file_path.name}")
        print(f"  크기: {stat.st_size} bytes")
        print(f"  확장자: {file_path.suffix}")
        print(f"  부모 디렉토리: {file_path.parent.name}")
        print(f"  절대 경로: {file_path.resolve()}")
    
    # 패턴 매칭으로 파일 찾기
    json_files = list(data_dir.glob("*.json"))
    print(f"\nJSON 파일들: {[f.name for f in json_files]}")
    
    # 파일 내용 읽고 처리
    total_count = 0
    for file_path in json_files:
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            print(f"\n{file_path.name} 내용:")
            for key, value in data.items():
                print(f"  {key}: {value}")
                if isinstance(value, int):
                    total_count += value
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {e}")
    
    print(f"\n모든 숫자값 합계: {total_count}")
    
    return data_dir

if __name__ == "__main__":
    # 프로젝트 구조 생성
    project = setup_restaurant_project()
    explore_project(project)
    
    # 파일 조작 예제
    temp_dir = file_operations_example()
    
    print(f"\n[O] 예제 실행 완료")
    print(f"생성된 디렉토리:")
    print(f"  - {project.resolve()}")
    print(f"  - {temp_dir.resolve()}")
