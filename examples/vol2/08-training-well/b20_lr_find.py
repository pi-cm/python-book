# [2권 Chapter 8. 학습 잘 시키기 · 8.11 손실이 안 줄 때 디버깅 · manuscript-vol2/chapters/08-training-well.md:1073]
import math

import matplotlib.pyplot as plt
import torch
from torch import nn

from 학습도구 import 데이터_준비, 모델_만들기

(X_학습, y_학습), _, _ = 데이터_준비(잡음_비율=0.0, 학습_개수=1000)
torch.manual_seed(0)
모델 = 모델_만들기()
시작_lr, 끝_lr, 단계_수 = 1e-6, 1.0, 100
옵티마이저 = torch.optim.Adam(모델.parameters(), lr=시작_lr)
배율 = (끝_lr / 시작_lr) ** (1 / 단계_수)      # 단계마다 학습률에 곱할 값

학습률들, 손실들 = [], []
평균 = None
for 단계 in range(단계_수):
    순서 = torch.randint(0, len(X_학습), (32,))
    옵티마이저.zero_grad()
    손실 = nn.functional.cross_entropy(모델(X_학습[순서]), y_학습[순서])
    손실.backward()
    옵티마이저.step()
    평균 = 손실.item() if 평균 is None else 0.9 * 평균 + 0.1 * 손실.item()   # 흔들림 줄이기
    학습률들.append(옵티마이저.param_groups[0]["lr"])
    손실들.append(평균)
    if not math.isfinite(평균) or 평균 > 4 * min(손실들):
        break                                 # 손실이 폭발하면 그만
    for 그룹 in 옵티마이저.param_groups:
        그룹["lr"] *= 배율

for i in range(0, len(학습률들), 20):
    print(f"학습률 {학습률들[i]:9.2e}  손실 {손실들[i]:.4f}")
print(f"마지막: 학습률 {학습률들[-1]:.2e}, 손실 {손실들[-1]:.4f}")
최저 = min(range(len(손실들)), key=손실들.__getitem__)
print(f"손실이 가장 낮았던 학습률: {학습률들[최저]:.2e}")

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False
plt.figure(figsize=(7, 3.5))
plt.plot(학습률들, 손실들)
plt.xscale("log")
눈금 = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1]
plt.xticks(눈금, [f"{v:g}" for v in 눈금])     # 눈금 글자를 1e-06, 0.01처럼
plt.xlabel("학습률 (로그 눈금)")
plt.ylabel("손실 (이동 평균)")
plt.tight_layout()
plt.savefig("lr_finder.png", dpi=200)
