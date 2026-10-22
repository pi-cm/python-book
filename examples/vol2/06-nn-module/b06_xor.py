# [2권 Chapter 6. nn.Module과 학습 루프: 모든 모델이 따르는 표준형 · 6.2 활성화 함수: 직선을 구부리는 장치 · manuscript-vol2/chapters/06-nn-module.md:238]
import torch
from torch import nn

# XOR: 두 입력이 다를 때만 1
X = torch.tensor([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
y = torch.tensor([[0.0], [1.0], [1.0], [0.0]])


def 학습하기(모델: nn.Module, 단계: int = 2000) -> nn.Module:
    """XOR 네 점으로 모델을 학습한다(한 줄씩은 6.7절에서 본다)."""
    손실함수 = nn.BCEWithLogitsLoss()
    옵티마이저 = torch.optim.Adam(모델.parameters(), lr=0.05)
    for _ in range(단계):
        옵티마이저.zero_grad()
        손실 = 손실함수(모델(X), y)
        손실.backward()
        옵티마이저.step()
    return 모델


후보 = {
    "선형 한 층": lambda: nn.Linear(2, 1),
    "선형 두 층": lambda: nn.Sequential(nn.Linear(2, 4), nn.Linear(4, 1)),
    "선형+ReLU+선형": lambda: nn.Sequential(nn.Linear(2, 4), nn.ReLU(), nn.Linear(4, 1)),
}
for 이름, 만들기 in 후보.items():
    torch.manual_seed(1)
    모델 = 학습하기(만들기())
    with torch.no_grad():                       # 결과만 볼 때는 계산 기록을 끈다(6.8절)
        확률 = torch.sigmoid(모델(X)).squeeze(1)
    맞힘 = ((확률 > 0.5).float() == y.squeeze(1)).sum().item()
    print(f"{이름}: 확률 {확률.round(decimals=3).tolist()}, 맞힘 {맞힘:.0f}/4")
print("정답:", y.squeeze(1).int().tolist())
