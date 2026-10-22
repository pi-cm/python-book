# [1권 Chapter 14: 모듈과 패키지 · 14.8 uv를 활용한 현대적 패키지 관리 · manuscript/chapters/14-modules-packages.md:1410]
# performance_comparison.py
"""uv vs pip 성능 비교"""
import time
import subprocess

def time_command(cmd):
    """명령 실행 시간 측정"""
    start = time.time()
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    end = time.time()
    return end - start, result.returncode

# 가상환경 생성 속도 비교
print("=== 가상환경 생성 속도 비교 ===")

# uv (매우 빠름)
uv_time, _ = time_command("uv venv test-uv --python 3.11")
print(f"uv venv 생성: {uv_time:.2f}초")

# python -m venv (느림)
venv_time, _ = time_command("python -m venv test-venv")
print(f"python venv 생성: {venv_time:.2f}초")

if uv_time > 0:
    print(f"uv가 {venv_time/uv_time:.1f}배 빠름")

# 의존성 해결 속도도 uv가 훨씬 빠름
print("\n=== uv의 주요 장점 ===")
print("1. 속도: Rust로 작성되어 매우 빠름")
print("2. 호환성: pip와 호환되는 API")
print("3. 의존성 해결: 더 정확하고 빠른 해결")
print("4. 캐싱: 효율적인 캐시 시스템")
print("5. 프로젝트 관리: pyproject.toml 기반 현대적 관리")
print("6. 멀티플랫폼: Windows, macOS, Linux 모두 지원")
print("7. 메모리 효율성: 메모리 사용량 최적화")

# 실제 사용 예제
print("\n=== 실제 워크플로우 예제 ===")
workflow_commands = [
    "# 새 프로젝트 시작",
    "uv init seoul-restaurant-api",
    "cd seoul-restaurant-api",
    "",
    "# 의존성 추가",
    "uv add fastapi uvicorn pydantic",
    "uv add --dev pytest black ruff",
    "",
    "# 개발 서버 실행",
    "uv run uvicorn main:app --reload",
    "",
    "# 테스트 실행",
    "uv run pytest",
    "",
    "# 코드 품질 검사",
    "uv run black .",
    "uv run ruff check .",
]

for cmd in workflow_commands:
    print(cmd)
