# [2권 Chapter 1. 머신러닝이란: 규칙을 짜지 않고 데이터로 배우기 · 1.8 특성의 눈금 맞추기 · manuscript-vol2/chapters/01-what-is-ml.md:841]
import numpy as np
from sklearn.neighbors import KNeighborsClassifier

# 고객 400명의 나이(세)와 연소득(만 원). 예제용으로 만든 데이터다.
rng = np.random.default_rng(0)
나이 = rng.uniform(20, 60, 400)
연소득 = rng.uniform(2000, 8000, 400)
X = np.column_stack([나이, 연소득])
y = (나이 > 40).astype(int)          # 구매 여부는 나이로만 정해진다고 하자

X_학습, X_테스트 = X[:300], X[300:]
y_학습, y_테스트 = y[:300], y[300:]

그대로 = KNeighborsClassifier(n_neighbors=5).fit(X_학습, y_학습)
print(f"그대로:    정확도 {그대로.score(X_테스트, y_테스트):.3f}")

# 학습 데이터의 평균과 표준편차로 두 특성의 눈금을 맞춘다 (표준화)
평균, 표준편차 = X_학습.mean(axis=0), X_학습.std(axis=0)
표준화 = KNeighborsClassifier(n_neighbors=5).fit((X_학습 - 평균) / 표준편차, y_학습)
print(f"표준화 후: 정확도 {표준화.score((X_테스트 - 평균) / 표준편차, y_테스트):.3f}")
print("특성별 표준편차(나이, 연소득):", 표준편차.round(1))
