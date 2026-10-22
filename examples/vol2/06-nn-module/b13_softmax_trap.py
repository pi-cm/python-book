# [2권 Chapter 6. nn.Module과 학습 루프: 모든 모델이 따르는 표준형 · 6.5 손실 함수: 얼마나 틀렸나 · manuscript-vol2/chapters/06-nn-module.md:572]
import torch
from torch import nn

손실함수 = nn.CrossEntropyLoss()
정답 = torch.tensor([0])                       # 0번 클래스가 정답

for 점수 in [1.0, 3.0, 10.0]:
    로짓 = torch.tensor([[점수, 0.0, 0.0]])     # 점점 더 확신하는 모델
    바르게 = 손실함수(로짓, 정답)
    잘못 = 손실함수(torch.softmax(로짓, dim=1), 정답)   # 소프트맥스를 미리 씌움
    print(f"정답 점수 {점수:4}: 로짓을 넣으면 {바르게:.4f}, 확률을 넣으면 {잘못:.4f}")
