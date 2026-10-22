# [2권 Chapter 6. nn.Module과 학습 루프: 모든 모델이 따르는 표준형 · 6.4 파라미터 들여다보기 · manuscript-vol2/chapters/06-nn-module.md:445]
import torch
from torch import nn

모델 = nn.Sequential(
    nn.Flatten(),
    nn.Linear(784, 256),
    nn.ReLU(),
    nn.Linear(256, 10),
)
for 이름, p in 모델.named_parameters():
    print(f"{이름:9} {str(tuple(p.shape)):11} {p.numel():>8,}개")

전체 = sum(p.numel() for p in 모델.parameters())
print(f"전체 {전체:,}개 = {784 * 256 + 256 + 256 * 10 + 10:,}개")
print(f"float32로 약 {전체 * 4 / 1024**2:.2f}MB")

# 첫 층을 얼려 두면(학습하지 않게 하면)?
for p in 모델[1].parameters():
    p.requires_grad_(False)
학습_대상 = sum(p.numel() for p in 모델.parameters() if p.requires_grad)
print(f"학습 대상 {학습_대상:,}개")
