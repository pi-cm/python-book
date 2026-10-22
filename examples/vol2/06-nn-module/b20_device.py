# [2권 Chapter 6. nn.Module과 학습 루프: 모든 모델이 따르는 표준형 · 6.9 장치로 옮기기 · manuscript-vol2/chapters/06-nn-module.md:932]
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
모델 = nn.Linear(3, 1)
옮긴_모델 = 모델.to(장치)                      # 모델은 제자리에서 옮겨진다
print("같은 객체인가:", 옮긴_모델 is 모델)
print("파라미터 위치:", next(모델.parameters()).device)

x = torch.rand(2, 3)                          # 데이터는 아직 CPU에
try:
    모델(x)
except RuntimeError as e:
    print("오류:", e)

x = x.to(장치)                                 # 텐서는 새 텐서를 돌려주니 다시 받는다
print(모델(x).detach().cpu())       # 결과를 CPU로 가져와 보기
