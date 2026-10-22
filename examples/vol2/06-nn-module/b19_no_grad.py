# [2권 Chapter 6. nn.Module과 학습 루프: 모든 모델이 따르는 표준형 · 6.8 평가 루프: 학습 모드와 평가 모드 · manuscript-vol2/chapters/06-nn-module.md:881]
import torch
from torch import nn

torch.manual_seed(0)
모델 = nn.Linear(1000, 1000)
x = torch.rand(64, 1000)

출력 = 모델(x)
print("기록함   :", 출력.requires_grad, type(출력.grad_fn).__name__)

with torch.no_grad():
    출력 = 모델(x)
print("기록 안 함:", 출력.requires_grad, 출력.grad_fn)


def 정확도_재기(모델: nn.Module, X: torch.Tensor, y: torch.Tensor) -> float:
    """분류 모델의 정확도를 잰다. 평가 루프의 표준형."""
    모델.eval()                                 # 1) 평가 모드로
    with torch.no_grad():                       # 2) 계산 기록 끄기
        예측 = 모델(X).argmax(dim=1)            # 3) 가장 높은 점수의 클래스
    return (예측 == y).float().mean().item()


분류기 = nn.Sequential(nn.Linear(2, 8), nn.ReLU(), nn.Linear(8, 3))
X = torch.randn(100, 2)
y = torch.randint(0, 3, (100,))
print(f"학습 전 정확도: {정확도_재기(분류기, X, y):.0%}")
print("다시 학습 모드로 되돌렸나:", 분류기.training)
