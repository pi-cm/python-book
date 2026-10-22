# [2권 Chapter 6. nn.Module과 학습 루프: 모든 모델이 따르는 표준형 · 6.5 손실 함수: 얼마나 틀렸나 · manuscript-vol2/chapters/06-nn-module.md:493]
import torch
from torch import nn

예측 = torch.tensor([2.5, 0.0, 2.0, 8.0])     # 집값 예측(억 원, 예제용)
정답 = torch.tensor([3.0, -0.5, 2.0, 7.0])

손실함수 = nn.MSELoss()
print("MSE :", 손실함수(예측, 정답))
print("손으로:", ((예측 - 정답) ** 2).mean())
print("MAE :", nn.L1Loss()(예측, 정답))

# 모양이 (4, 1)과 (4,)로 어긋나면?
어긋난_예측 = 예측.unsqueeze(1)                 # 모델 출력은 보통 (묶음, 1)
print("어긋난 모양:", 손실함수(어긋난_예측, 정답))
print("맞춘 모양 :", 손실함수(어긋난_예측.squeeze(1), 정답))
