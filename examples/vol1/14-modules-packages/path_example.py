# [1권 Chapter 14: 모듈과 패키지 · 14.7 모듈 검색 경로 · manuscript/chapters/14-modules-packages.md:1017]
# path_example.py
import sys
import os

print("=== 파이썬 모듈 검색 경로 ===")
for i, path in enumerate(sys.path):
    print(f"{i+1:2d}. {path}")

print(f"\n현재 작업 디렉토리: {os.getcwd()}")
print(f"현재 파일 위치: {__file__}")

# 경로 추가하기
custom_path = "/Users/me/my_modules"
if custom_path not in sys.path:
    sys.path.append(custom_path)
    print(f"\n사용자 정의 경로 추가: {custom_path}")

# 경로 우선순위 변경 (맨 앞에 추가)
priority_path = "/Users/me/priority_modules"  
sys.path.insert(0, priority_path)
print(f"우선순위 경로 추가: {priority_path}")

print("\n=== 업데이트된 검색 경로 ===")
for i, path in enumerate(sys.path[:5]):  # 상위 5개만 표시
    print(f"{i+1:2d}. {path}")
