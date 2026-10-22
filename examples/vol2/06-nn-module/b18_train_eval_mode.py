# [2권 Chapter 6. nn.Module과 학습 루프: 모든 모델이 따르는 표준형 · 6.8 평가 루프: 학습 모드와 평가 모드 · manuscript-vol2/chapters/06-nn-module.md:843]
import torch
from torch import nn

torch.manual_seed(0)
모델 = nn.Sequential(nn.Linear(4, 4), nn.Dropout(p=0.5))   # 드롭아웃: 8장에서 자세히
x = torch.ones(1, 4)

모델.train()                                    # 학습 모드(처음 만들면 이 모드)
print("학습 모드:", 모델.training)
print(모델(x))
print(모델(x))                                   # 같은 입력인데 결과가 다르다

모델.eval()                                     # 평가 모드
print("평가 모드:", 모델.training, 모델[1].training)
print(모델(x))
print(모델(x))
