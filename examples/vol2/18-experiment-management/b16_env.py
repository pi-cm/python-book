# [2권 Chapter 18. 실험 관리와 재현성 · 18.7 데이터·코드·환경 버전 기록 · manuscript-vol2/chapters/18-experiment-management.md:1205]
import hashlib
import importlib.metadata
import platform
import sys
from pathlib import Path

import torch


def 장치_고르기() -> torch.device:
    """쓸 수 있는 가장 빠른 장치를 고른다."""
    if torch.cuda.is_available():
        return torch.device("cuda")       # NVIDIA GPU
    if torch.backends.mps.is_available():
        return torch.device("mps")        # Apple 실리콘 GPU
    return torch.device("cpu")


def 환경_기록(패키지들: list[str], 잠금_파일: Path = Path("uv.lock")) -> dict:
    """결과에 영향을 줄 수 있는 실행 환경을 딕셔너리 하나로."""
    기록 = {
        "파이썬": platform.python_version(),
        "운영체제": f"{platform.system()} {platform.release()} ({platform.machine()})",
        "패키지": {이름: importlib.metadata.version(이름) for 이름 in 패키지들},
        "쓸 수 있는 장치": str(장치_고르기()),
        "CPU 스레드": torch.get_num_threads(),
        "CUDA": torch.version.cuda,                         # CUDA가 없는 PyTorch면 None
    }
    if 잠금_파일.exists():                                    # uv.lock이 있으면 그 지문까지
        기록["uv.lock"] = hashlib.sha256(잠금_파일.read_bytes()).hexdigest()[:16]
    return 기록


for 키, 값 in 환경_기록(["torch", "numpy", "torchvision", "optuna", "mlflow"]).items():
    print(f"{키}: {값}")
print("실행한 명령:", " ".join([Path(sys.argv[0]).name, *sys.argv[1:]]))
