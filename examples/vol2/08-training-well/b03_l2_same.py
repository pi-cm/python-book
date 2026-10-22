# [2권 Chapter 8. 학습 잘 시키기 · 8.2 가중치 감쇠(weight decay) · manuscript-vol2/chapters/08-training-well.md:260]
import torch
from torch import nn

torch.manual_seed(0)
X, y = torch.randn(8, 3), torch.randn(8, 1)
벌점_세기 = 0.1

# 방법 1: 손실에 (모든 가중치 제곱의 합) × 벌점_세기 / 2를 직접 더한다
torch.manual_seed(1)
모델1 = nn.Linear(3, 1)
옵티마이저1 = torch.optim.SGD(모델1.parameters(), lr=0.1)
벌점 = sum((p ** 2).sum() for p in 모델1.parameters())
손실1 = nn.functional.mse_loss(모델1(X), y) + 벌점_세기 / 2 * 벌점
손실1.backward()
옵티마이저1.step()

# 방법 2: 옵티마이저의 weight_decay 옵션에 맡긴다
torch.manual_seed(1)
모델2 = nn.Linear(3, 1)
옵티마이저2 = torch.optim.SGD(모델2.parameters(), lr=0.1, weight_decay=벌점_세기)
손실2 = nn.functional.mse_loss(모델2(X), y)
손실2.backward()
옵티마이저2.step()

print("방법 1 가중치:", 모델1.weight.data)
print("방법 2 가중치:", 모델2.weight.data)
print("같은가?", torch.allclose(모델1.weight, 모델2.weight))
