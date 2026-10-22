"""1권 Chapter 17: 표준 라이브러리 핵심 가이드 — 시스템과 OS 인터페이스

원고: manuscript/chapters/17-standard-library-guide.md (1078줄부터)
"""

# ---- 원고 1078줄 ----
import sys
import os
import platform
import subprocess

# 시스템 정보 출력
print("=== 한국어 시스템 정보 ===")
print(f"파이썬 버전: {sys.version}")
print(f"운영체제: {platform.system()} {platform.release()}")
print(f"프로세서: {platform.processor()}")
print(f"현재 작업 디렉토리: {os.getcwd()}")
print(f"파이썬 경로: {sys.executable}")

# 한국어 환경변수 설정
os.environ['한국_서비스_설정'] = 'production'
os.environ['LANG'] = 'ko_KR.UTF-8'

print(f"\n언어 설정: {os.environ.get('LANG', '설정되지 않음')}")
print(f"서비스 설정: {os.environ.get('한국_서비스_설정', '기본값')}")

# 시스템 명령 실행
def run_korean_command(command, description):
    """한국어 설명과 함께 시스템 명령 실행"""
    print(f"\n[{description}]")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print(f"성공: {result.stdout.strip()}")
        else:
            print(f"실패: {result.stderr.strip()}")
    except Exception as e:
        print(f"오류: {str(e)}")

# 시스템 정보 수집
if platform.system() == "Darwin":  # macOS
    run_korean_command("sw_vers", "macOS 버전 확인")
    run_korean_command("uptime", "시스템 가동 시간")
elif platform.system() == "Linux":
    run_korean_command("lsb_release -a", "리눅스 배포판 확인")
    run_korean_command("df -h", "디스크 사용량 확인")

# 메모리 사용량 모니터링 (외부 패키지 psutil 필요)
def get_system_status():
    """시스템 상태 정보 수집"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "CPU 사용률": f"{cpu_percent}%",
        "메모리 사용률": f"{memory.percent}%",
        "메모리 사용량": f"{memory.used / (1024**3):.1f}GB / {memory.total / (1024**3):.1f}GB",
        "디스크 사용률": f"{disk.percent}%",
        "디스크 여유공간": f"{disk.free / (1024**3):.1f}GB"
    }

try:
    import psutil
    print("\n=== 시스템 리소스 현황 ===")
    status = get_system_status()
    for key, value in status.items():
        print(f"{key}: {value}")
except ImportError:
    print("psutil 패키지가 설치되지 않음 (uv add psutil)")
