# [2권 Chapter 8. 학습 잘 시키기 · 8.11 손실이 안 줄 때 디버깅 · manuscript-vol2/chapters/08-training-well.md:1242]
import torch
from torch import nn

from 학습도구 import 데이터_준비, 모델_만들기, 평가

(X_학습, y_학습), (X_검증, y_검증), _ = 데이터_준비(잡음_비율=0.0, 학습_개수=1000)

for 소프트맥스_추가 in (False, True):
    torch.manual_seed(0)
    모델 = 모델_만들기()
    if 소프트맥스_추가:
        모델.append(nn.Softmax(dim=1))        # 모델 끝에 소프트맥스를 붙였다
    옵티마이저 = torch.optim.Adam(모델.parameters(), lr=1e-3)
    for 단계 in range(300):
        옵티마이저.zero_grad()
        손실 = nn.CrossEntropyLoss()(모델(X_학습), y_학습)   # 안에서 또 소프트맥스
        손실.backward()
        옵티마이저.step()
    _, 정확도 = 평가(모델, X_검증, y_검증)
    print(f"소프트맥스 {'두 번' if 소프트맥스_추가 else '한 번'}: 학습 손실 {손실.item():.4f}, 검증 정확도 {정확도:.1%}")

# 확률이 완벽한 원-핫이어도 소프트맥스를 한 번 더 거치면 손실은 이 아래로 못 내려간다
완벽 = torch.zeros(1, 10)
완벽[0, 3] = 1.0
print(f"넘을 수 없는 바닥: {nn.CrossEntropyLoss()(완벽, torch.tensor([3])).item():.4f}")
