# [2권 Chapter 1. 머신러닝이란: 규칙을 짜지 않고 데이터로 배우기 · 1.5 첫 모델: 최근접 이웃 분류 · manuscript-vol2/chapters/01-what-is-ml.md:380]
import numpy as np
from sklearn.datasets import load_iris

X, y = load_iris(return_X_y=True)
새_꽃 = np.array([6.0, 2.9, 4.6, 1.5])   # 정답을 모르는 꽃 한 송이 (예제용)

차이 = X - 새_꽃                         # (150, 4) - (4,) → 브로드캐스팅
거리 = np.sqrt((차이 ** 2).sum(axis=1))  # 꽃마다 거리 하나 → (150,)
print("거리 모양:", 거리.shape)

가까운_순 = np.argsort(거리)[:5]          # 가까운 다섯 송이의 번호
for 번호 in 가까운_순:
    print(f"{번호:3d}번 꽃  거리 {거리[번호]:.3f}  레이블 {y[번호]}")
print("다섯 이웃의 표:", np.bincount(y[가까운_순], minlength=3))
