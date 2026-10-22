# [2권 Chapter 6. nn.Module과 학습 루프: 모든 모델이 따르는 표준형 · 6.6 옵티마이저: 어떻게 고칠까 · manuscript-vol2/chapters/06-nn-module.md:615]
import torch
from torch import nn

torch.manual_seed(0)
층 = nn.Linear(2, 1)
옵티마이저 = torch.optim.SGD(층.parameters(), lr=0.1)

x = torch.tensor([[1.0, 2.0]])
y = torch.tensor([[1.0]])
손실 = nn.MSELoss()(층(x), y)
손실.backward()                                # 기울기 계산(5장)

이전 = 층.weight.detach().clone()
기울기 = 층.weight.grad.clone()
옵티마이저.step()                               # 파라미터 고치기

print("고치기 전:", 이전)
print("기울기   :", 기울기)
print("고친 뒤  :", 층.weight.detach())
print("이전 - 0.1 × 기울기와 같은가:", torch.allclose(층.weight.detach(), 이전 - 0.1 * 기울기))
