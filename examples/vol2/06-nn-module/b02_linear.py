# [2권 Chapter 6. nn.Module과 학습 루프: 모든 모델이 따르는 표준형 · 6.1 층 하나: 입력 @ 가중치 + 편향 · manuscript-vol2/chapters/06-nn-module.md:81]
import torch
from torch import nn

torch.manual_seed(0)
층 = nn.Linear(3, 2)                 # 입력 3개 → 출력 2개
print(층)
print("weight:", 층.weight.shape, "bias:", 층.bias.shape)

x = torch.rand(4, 3)
print(층(x))
직접 = x @ 층.weight.T + 층.bias      # 손으로 같은 계산
print("같은가:", torch.allclose(층(x), 직접))
print("학습 대상인가:", 층.weight.requires_grad)
