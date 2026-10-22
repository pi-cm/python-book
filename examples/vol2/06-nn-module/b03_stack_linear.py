# [2권 Chapter 6. nn.Module과 학습 루프: 모든 모델이 따르는 표준형 · 6.1 층 하나: 입력 @ 가중치 + 편향 · manuscript-vol2/chapters/06-nn-module.md:118]
import torch
from torch import nn

torch.manual_seed(0)
층1 = nn.Linear(3, 5)
층2 = nn.Linear(5, 2)
x = torch.rand(4, 3)

두_층 = 층2(층1(x))

# 두 층을 합친 가중치 하나, 편향 하나
W = 층2.weight @ 층1.weight                # (2, 5) @ (5, 3) → (2, 3)
b = 층2.weight @ 층1.bias + 층2.bias        # (2,)
한_층 = x @ W.T + b

print(두_층)
print(한_층)
print("같은가:", torch.allclose(두_층, 한_층, atol=1e-6))
