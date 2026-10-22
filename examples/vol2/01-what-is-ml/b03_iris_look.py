# [2권 Chapter 1. 머신러닝이란: 규칙을 짜지 않고 데이터로 배우기 · 1.2 데이터를 표로 보기: 샘플, 특성, 레이블 · manuscript-vol2/chapters/01-what-is-ml.md:150]
import numpy as np
from sklearn.datasets import load_iris

붓꽃 = load_iris()
X, y = 붓꽃.data, 붓꽃.target

print("X 모양:", X.shape, " y 모양:", y.shape)
print("특성 이름:", 붓꽃.feature_names)
print("레이블 이름:", 붓꽃.target_names.tolist())
for i in [0, 50, 100]:
    print(f"{i:3d}번 꽃: 특성 {X[i]} → 레이블 {y[i]} ({붓꽃.target_names[y[i]]})")
print("레이블별 개수:", np.bincount(y))
