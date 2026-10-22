# [2권 Chapter 8. 학습 잘 시키기 · 8.11 손실이 안 줄 때 디버깅 · manuscript-vol2/chapters/08-training-well.md:1023]
import torch
from torch import nn

from 학습도구 import 데이터_준비, 모델_만들기

(X_학습, y_학습), _, _ = 데이터_준비(잡음_비율=0.0)
X_한배치, y_한배치 = X_학습[:32], y_학습[:32]     # 배치 딱 하나


def 한_배치_과적합(버그: bool) -> None:
    torch.manual_seed(0)
    모델 = 모델_만들기()
    옵티마이저 = torch.optim.Adam(모델.parameters(), lr=1e-3)
    if 버그:
        모델 = 모델_만들기()                  # 옵티마이저를 만든 뒤 모델을 다시 만들었다!
    for 단계 in range(201):
        옵티마이저.zero_grad()
        손실 = nn.functional.cross_entropy(모델(X_한배치), y_한배치)
        손실.backward()
        옵티마이저.step()
        if 단계 in (0, 50, 100, 200):
            print(f"  {단계:3d}단계 손실 {손실.item():.4f}")


print("정상 코드")
한_배치_과적합(버그=False)
print("버그가 있는 코드")
한_배치_과적합(버그=True)
