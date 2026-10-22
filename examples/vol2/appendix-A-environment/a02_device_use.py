# [2권 부록 A. 실행 환경 만들기 · A.6 장치 고르기와 설치 확인 스크립트 · manuscript-vol2/appendix/A-environment.md:214]
import torch
from torch import nn


def 장치_고르기() -> torch.device:
    """쓸 수 있는 가장 빠른 장치를 고른다."""
    if torch.cuda.is_available():
        return torch.device("cuda")       # NVIDIA GPU
    if torch.backends.mps.is_available():
        return torch.device("mps")        # Apple 실리콘 GPU
    return torch.device("cpu")


장치 = 장치_고르기()
torch.manual_seed(0)
모델 = nn.Linear(4, 2).to(장치)            # 1) 모델을 장치로 (6장 6.9절)
x = torch.randn(8, 4).to(장치)              # 2) 데이터도 같은 장치로
출력 = 모델(x)
print(출력.device, tuple(출력.shape))
print(출력.argmax(dim=1).cpu().tolist())    # 3) 출력은 CPU로 꺼내서 파이썬 값으로
