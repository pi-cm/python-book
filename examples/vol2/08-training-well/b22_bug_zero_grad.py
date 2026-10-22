# [2권 Chapter 8. 학습 잘 시키기 · 8.11 손실이 안 줄 때 디버깅 · manuscript-vol2/chapters/08-training-well.md:1197]
import torch
from torch import nn

from 학습도구 import 데이터_준비, 로더_만들기, 모델_만들기, 평가

# backward()는 그래디언트를 덮어쓰지 않고 더한다
w = torch.tensor(1.0, requires_grad=True)
for 번 in range(1, 4):
    (3 * w).backward()                        # d(3w)/dw = 3
    print(f"{번}번째 backward 뒤 w.grad = {w.grad.item()}")

(X_학습, y_학습), (X_검증, y_검증), _ = 데이터_준비(잡음_비율=0.0, 학습_개수=1000)
for 비울까 in (True, False):
    torch.manual_seed(0)
    로더 = 로더_만들기(X_학습, y_학습)
    모델 = 모델_만들기()
    옵티마이저 = torch.optim.Adam(모델.parameters(), lr=1e-3)
    기록 = []
    for 에폭 in range(1, 21):
        모델.train()
        for X, y in 로더:
            if 비울까:
                옵티마이저.zero_grad()        # 이 한 줄이 없으면?
            nn.functional.cross_entropy(모델(X), y).backward()
            옵티마이저.step()
        if 에폭 in (1, 2, 3, 5, 10, 15, 20):
            기록.append(f"{에폭}에폭 {평가(모델, X_검증, y_검증)[1]:.0%}")
    print("zero_grad 있음:" if 비울까 else "zero_grad 없음:", ", ".join(기록))
