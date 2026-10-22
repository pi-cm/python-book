# [1권 Chapter 14: 모듈과 패키지 · 정리 및 베스트 프랙티스 · manuscript/chapters/14-modules-packages.md:2940]
# practical_tips.py
"""실전에서 유용한 팁들"""

import sys
import importlib
import inspect
from pathlib import Path

# 1. 동적 모듈 로딩
def load_plugin(plugin_name: str, plugin_dir: Path):
    """플러그인 동적 로딩"""
    sys.path.insert(0, str(plugin_dir))
    try:
        module = importlib.import_module(plugin_name)
        return module
    except ImportError as e:
        print(f"플러그인 로딩 실패: {e}")
        return None
    finally:
        if str(plugin_dir) in sys.path:
            sys.path.remove(str(plugin_dir))

# 2. 모듈 리로딩 (개발 시 유용)
def reload_module(module):
    """모듈 리로딩"""
    return importlib.reload(module)

# 3. 모듈 정보 탐색
def inspect_module(module):
    """모듈 내용 탐색"""
    print(f"=== {module.__name__} 모듈 정보 ===")
    
    # 모든 속성 나열
    for name in dir(module):
        if not name.startswith('_'):
            obj = getattr(module, name)
            obj_type = type(obj).__name__
            
            # 함수인 경우 시그니처도 표시
            if inspect.isfunction(obj):
                sig = inspect.signature(obj)
                print(f"함수: {name}{sig}")
            elif inspect.isclass(obj):
                print(f"클래스: {name}")
                # 클래스 메서드들도 표시
                for method_name in dir(obj):
                    if not method_name.startswith('_'):
                        method = getattr(obj, method_name)
                        if inspect.ismethod(method) or inspect.isfunction(method):
                            print(f"  메서드: {method_name}")
            else:
                print(f"{obj_type}: {name}")

# 4. 패키지 구조 시각화
def print_package_structure(package_path: Path, prefix: str = ""):
    """패키지 구조를 트리 형태로 출력"""
    if not package_path.is_dir():
        return
    
    items = sorted(package_path.iterdir())
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        current_prefix = "└── " if is_last else "├── "
        
        if item.is_dir() and (item / "__init__.py").exists():
            print(f"{prefix}{current_prefix}{item.name}/")
            next_prefix = prefix + ("    " if is_last else "│   ")
            print_package_structure(item, next_prefix)
        elif item.suffix == '.py':
            print(f"{prefix}{current_prefix}{item.name}")
        elif item.is_dir():
            print(f"{prefix}{current_prefix}{item.name}/")

# 5. 순환 import 감지 (간단한 버전)
def find_circular_imports(package_path: Path):
    """순환 import 감지"""
    import ast
    
    imports = {}  # 파일별 import 목록
    
    for py_file in package_path.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            file_imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        file_imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        file_imports.append(node.module)
            
            imports[py_file.stem] = file_imports
            
        except Exception as e:
            print(f"파일 파싱 오류 {py_file}: {e}")
    
    # 간단한 순환 감지 (실제로는 더 복잡한 알고리즘 필요)
    for module, module_imports in imports.items():
        for imported in module_imports:
            if imported in imports:
                imported_imports = imports[imported]
                if module in [imp.split('.')[-1] for imp in imported_imports]:
                    print(f"[!] 순환 import 감지: {module} ↔ {imported}")

if __name__ == "__main__":
    # 예제 실행
    print("=== 패키지 구조 출력 ===")
    seoul_pkg = Path("seoul_restaurants")
    if seoul_pkg.exists():
        print_package_structure(seoul_pkg)
    
    print("\n=== 순환 import 검사 ===") 
    find_circular_imports(Path("seoul_restaurants"))
