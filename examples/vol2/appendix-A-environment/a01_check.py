# [2권 부록 A. 실행 환경 만들기 · A.6 장치 고르기와 설치 확인 스크립트 · manuscript-vol2/appendix/A-environment.md:248]
# 설치_확인.py: 새 컴퓨터에서 가장 먼저 실행해 보는 점검 스크립트
import platform
import sys

import torch


def 장치_고르기() -> torch.device:
    """쓸 수 있는 가장 빠른 장치를 고른다."""
    if torch.cuda.is_available():
        return torch.device("cuda")       # NVIDIA GPU
    if torch.backends.mps.is_available():
        return torch.device("mps")        # Apple 실리콘 GPU
    return torch.device("cpu")


print("파이썬     :", sys.version.split()[0])
print("운영체제   :", platform.system(), platform.machine())
print("PyTorch    :", torch.__version__)
print("CUDA 빌드  :", torch.version.cuda)            # CPU·MPS용 빌드면 None
print("CUDA 사용  :", torch.cuda.is_available())
if torch.cuda.is_available():
    print("GPU 이름   :", torch.cuda.get_device_name(0))
print("MPS 사용   :", torch.backends.mps.is_available())

장치 = 장치_고르기()
print("고른 장치  :", 장치)

# 같은 계산을 CPU와 고른 장치에서 해 보고 결과를 비교한다
torch.manual_seed(0)
a = torch.randn(512, 512)
b = torch.randn(512, 512)
cpu_결과 = a @ b
장치_결과 = (a.to(장치) @ b.to(장치)).cpu()
print("행렬 곱 모양:", tuple(장치_결과.shape))
print("CPU와 같은가:", torch.allclose(cpu_결과, 장치_결과, atol=1e-3))
