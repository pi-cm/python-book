# [2권 Chapter 6. nn.Module과 학습 루프: 모든 모델이 따르는 표준형 · 6.7 표준 학습 루프: 다섯 줄의 반복 · manuscript-vol2/chapters/06-nn-module.md:722]
import numpy as np
import torch
from torch import nn

# 5장 5.7절의 아이스크림 판매 데이터(예제용으로 만든 데이터)
rng = np.random.default_rng(0)
기온 = rng.uniform(18, 34, size=30).round(1)
판매량 = (2.5 * 기온 - 15 + rng.normal(0, 4, size=30)).round()
x = torch.tensor((기온 - 기온.mean()) / 기온.std(), dtype=torch.float32).unsqueeze(1)  # (30, 1)
y = torch.tensor(판매량, dtype=torch.float32).unsqueeze(1)                             # (30, 1)

모델 = nn.Linear(1, 1)                          # w * x + b
nn.init.zeros_(모델.weight)                      # 5장처럼 0에서 출발
nn.init.zeros_(모델.bias)
손실함수 = nn.MSELoss()
옵티마이저 = torch.optim.SGD(모델.parameters(), lr=0.1)

기록 = []
for _ in range(30):
    옵티마이저.zero_grad()
    손실 = 손실함수(모델(x), y)
    손실.backward()
    옵티마이저.step()
    기록.append(손실.item())

print([round(v, 1) for v in 기록[::5]], "→", round(기록[-1], 1))
print(f"w = {모델.weight.item():.3f}, b = {모델.bias.item():.3f}")
