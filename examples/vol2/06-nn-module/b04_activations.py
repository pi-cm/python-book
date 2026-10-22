# [2권 Chapter 6. nn.Module과 학습 루프: 모든 모델이 따르는 표준형 · 6.2 활성화 함수: 직선을 구부리는 장치 · manuscript-vol2/chapters/06-nn-module.md:164]
import torch
from torch import nn

x = torch.linspace(-3, 3, 7)
print("입력      :", x)
print("ReLU      :", torch.relu(x))
print("시그모이드:", torch.sigmoid(x).round(decimals=3))
print("tanh      :", torch.tanh(x).round(decimals=3))

활성화 = nn.ReLU()                    # 층처럼 쓰는 모양
print("nn.ReLU   :", 활성화(x))
