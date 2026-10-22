# [2권 Chapter 6. nn.Module과 학습 루프: 모든 모델이 따르는 표준형 · 6.3 nn.Module로 모델 만들기 · manuscript-vol2/chapters/06-nn-module.md:400]
import torch
from torch import nn


class 리스트모델(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.층들 = [nn.Linear(4, 4) for _ in range(3)]               # 그냥 리스트

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        for 층 in self.층들:
            x = torch.relu(층(x))
        return x


class 모듈리스트모델(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.층들 = nn.ModuleList([nn.Linear(4, 4) for _ in range(3)])  # 등록되는 리스트

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        for 층 in self.층들:
            x = torch.relu(층(x))
        return x


for 모델 in [리스트모델(), 모듈리스트모델()]:
    개수 = sum(p.numel() for p in 모델.parameters())
    print(f"{type(모델).__name__}: 파라미터 {개수}개, 출력 {tuple(모델(torch.rand(2, 4)).shape)}")
