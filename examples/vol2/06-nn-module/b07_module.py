# [2권 Chapter 6. nn.Module과 학습 루프: 모든 모델이 따르는 표준형 · 6.3 nn.Module로 모델 만들기 · manuscript-vol2/chapters/06-nn-module.md:298]
import torch
from torch import nn


class 작은신경망(nn.Module):
    """입력 → 은닉층(ReLU) → 출력으로 이어지는 신경망."""

    def __init__(self, 입력수: int, 은닉수: int, 출력수: int) -> None:
        super().__init__()                      # nn.Module의 준비 작업부터
        self.층1 = nn.Linear(입력수, 은닉수)
        self.활성화 = nn.ReLU()
        self.층2 = nn.Linear(은닉수, 출력수)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """입력이 모델 안을 지나가는 길."""
        x = self.층1(x)
        x = self.활성화(x)
        return self.층2(x)


torch.manual_seed(0)
모델 = 작은신경망(입력수=4, 은닉수=8, 출력수=3)
print(모델)

x = torch.rand(5, 4)                    # 5개 묶음 × 특성 4개
출력 = 모델(x)                           # forward를 직접 부르지 않는다
print(출력.shape)
print("forward와 같은가:", torch.equal(출력, 모델.forward(x)))
