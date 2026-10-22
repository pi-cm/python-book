# [2권 Chapter 8. 학습 잘 시키기 · 8.7 학습률 스케줄러 · manuscript-vol2/chapters/08-training-well.md:733]
import torch
from torch.optim.lr_scheduler import ReduceLROnPlateau

가짜_가중치 = torch.zeros(1, requires_grad=True)
옵티마이저 = torch.optim.SGD([가짜_가중치], lr=0.1)
스케줄러 = ReduceLROnPlateau(옵티마이저, mode="min", factor=0.5, patience=2)

# 예제용 검증 손실: 처음엔 줄다가 0.50 근처에서 멈춘다
검증_손실들 = [0.90, 0.70, 0.55, 0.50, 0.51, 0.50, 0.52, 0.49, 0.50, 0.51, 0.50, 0.50]
for 에폭, 손실 in enumerate(검증_손실들, start=1):
    스케줄러.step(손실)                       # 검증 손실을 넘겨준다
    print(f"{에폭:2d}에폭 검증 손실 {손실:.2f} -> 학습률 {옵티마이저.param_groups[0]['lr']:.4f}")
