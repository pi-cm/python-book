# [2권 Chapter 6. nn.Module과 학습 루프: 모든 모델이 따르는 표준형 · 6.7 표준 학습 루프: 다섯 줄의 반복 · manuscript-vol2/chapters/06-nn-module.md:765]
import torch
from torch import nn


def 동심원_만들기(개수: int) -> tuple[torch.Tensor, torch.Tensor]:
    """안쪽 원(0번)과 바깥 고리(1번)에 흩어진 점. 예제용으로 만든 데이터."""
    반지름 = torch.cat([torch.rand(개수 // 2), 1.5 + torch.rand(개수 // 2)])
    각도 = torch.rand(개수) * 2 * torch.pi
    X = torch.stack([반지름 * torch.cos(각도), 반지름 * torch.sin(각도)], dim=1)
    X = X + 0.3 * torch.randn(개수, 2)                # 경계가 겹치도록 흔들기
    y = torch.cat([torch.zeros(개수 // 2), torch.ones(개수 // 2)]).long()
    return X, y


torch.manual_seed(0)
X, y = 동심원_만들기(1000)
순서 = torch.randperm(1000)                       # 섞은 뒤 800개 학습, 200개 시험
X_학습, y_학습 = X[순서[:800]], y[순서[:800]]
X_시험, y_시험 = X[순서[800:]], y[순서[800:]]

모델 = nn.Sequential(nn.Linear(2, 16), nn.ReLU(), nn.Linear(16, 16), nn.ReLU(), nn.Linear(16, 2))
손실함수 = nn.CrossEntropyLoss()
옵티마이저 = torch.optim.Adam(모델.parameters(), lr=0.01)
묶음_크기 = 32

for 에폭 in range(1, 21):
    모델.train()
    섞기 = torch.randperm(800)
    합계 = 0.0
    for 시작 in range(0, 800, 묶음_크기):
        번호 = 섞기[시작:시작 + 묶음_크기]
        xb, yb = X_학습[번호], y_학습[번호]

        옵티마이저.zero_grad()            # 1) 지난 기울기 지우기
        출력 = 모델(xb)                    # 2) 순전파: 예측하기
        손실 = 손실함수(출력, yb)          # 3) 얼마나 틀렸나 재기
        손실.backward()                    # 4) 역전파: 고칠 방향 계산
        옵티마이저.step()                  # 5) 파라미터 고치기

        합계 += 손실.item() * len(번호)
    if 에폭 in (1, 5, 10, 20):
        모델.eval()
        with torch.no_grad():
            정확도 = (모델(X_시험).argmax(dim=1) == y_시험).float().mean().item()
        print(f"에폭 {에폭:2}: 학습 손실 {합계 / 800:.4f}, 시험 정확도 {정확도:.1%}")
