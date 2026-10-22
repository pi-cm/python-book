# [2권 Chapter 8. 학습 잘 시키기 · 8.11 손실이 안 줄 때 디버깅 · manuscript-vol2/chapters/08-training-well.md:992]
import math

import torch
from torch import nn

from 학습도구 import 데이터_준비, 모델_만들기

(X_학습, y_학습), _, _ = 데이터_준비(잡음_비율=0.0)
print(f"찍기 수준의 손실 -ln(1/10) = {math.log(10):.4f}")

torch.manual_seed(0)
모델 = 모델_만들기()
with torch.no_grad():
    print(f"학습 전 손실(정상)       = {nn.functional.cross_entropy(모델(X_학습), y_학습).item():.4f}")
    모델[-1].weight.mul_(100)                 # 마지막 층 가중치를 100배로 (잘못된 초기화)
    print(f"학습 전 손실(출력이 큼)  = {nn.functional.cross_entropy(모델(X_학습), y_학습).item():.4f}")
