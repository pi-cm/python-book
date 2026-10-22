# [2권 Chapter 6. nn.Module과 학습 루프: 모든 모델이 따르는 표준형 · 6.5 손실 함수: 얼마나 틀렸나 · manuscript-vol2/chapters/06-nn-module.md:527]
import torch
from torch import nn

로짓 = torch.tensor([[2.0, 1.0, 0.1],          # 사진 2장 × 클래스 3개의 점수
                    [0.5, 0.5, 3.0]])
정답 = torch.tensor([0, 2])                    # 클래스 번호(int64)

손실함수 = nn.CrossEntropyLoss()
print("CrossEntropy:", 손실함수(로짓, 정답))

# 손으로: 정답 칸의 확률에 -log를 씌워 평균
확률 = torch.softmax(로짓, dim=1)
정답_확률 = 확률[torch.arange(2), 정답]
print("정답 칸 확률:", 정답_확률)
print("손으로      :", -torch.log(정답_확률).mean())

for p in [0.99, 0.9, 0.5, 0.1, 0.01]:
    print(f"정답 확률 {p:4}일 때 손실 {-torch.log(torch.tensor(p)):.3f}")
