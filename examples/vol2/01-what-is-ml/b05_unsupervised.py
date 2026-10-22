# [2권 Chapter 1. 머신러닝이란: 규칙을 짜지 않고 데이터로 배우기 · 1.3 머신러닝의 세 갈래 · manuscript-vol2/chapters/01-what-is-ml.md:240]
import numpy as np
from sklearn.cluster import KMeans
from sklearn.datasets import load_iris

X, y = load_iris(return_X_y=True)

# 레이블 y는 주지 않고 특성 X만 주면서 "비슷한 것끼리 세 묶음으로" 나누라고 한다
묶음 = KMeans(n_clusters=3, n_init=10, random_state=0).fit_predict(X)

# 다 나눈 뒤에야 실제 품종과 맞춰 본다
for 번호 in range(3):
    품종별 = np.bincount(y[묶음 == 번호], minlength=3)
    print(f"묶음 {번호}: setosa {품종별[0]:2d}, versicolor {품종별[1]:2d}, virginica {품종별[2]:2d}")
