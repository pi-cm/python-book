# [1권 Chapter 14: 모듈과 패키지 · 14.7 모듈 검색 경로 · manuscript/chapters/14-modules-packages.md:1065]
# module_finder.py
import sys
import os
from pathlib import Path

def find_module_path(module_name):
    """모듈 탐색 과정 시뮬레이션"""
    print(f"=== '{module_name}' 모듈 탐색 과정 ===")
    
    for i, search_path in enumerate(sys.path):
        print(f"\n{i+1}. 경로 확인: {search_path}")
        
        if not search_path or not os.path.exists(search_path):
            print("   → 경로가 존재하지 않음")
            continue
            
        # .py 파일 찾기
        py_file = Path(search_path) / f"{module_name}.py"
        if py_file.exists():
            print(f"   [O] 발견: {py_file}")
            return str(py_file)
        
        # 패키지 디렉토리 찾기
        pkg_dir = Path(search_path) / module_name
        if pkg_dir.is_dir():
            init_file = pkg_dir / "__init__.py"
            if init_file.exists():
                print(f"   [O] 패키지 발견: {pkg_dir}")
                return str(pkg_dir)
        
        print("   → 해당 경로에서 발견되지 않음")
    
    print(f"\n[X] '{module_name}' 모듈을 찾을 수 없습니다")
    return None

# 테스트
find_module_path("cafe_utils")
find_module_path("seoul_restaurants") 
find_module_path("json")  # 내장 모듈
find_module_path("nonexistent_module")
