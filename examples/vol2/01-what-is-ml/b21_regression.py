# [2권 Chapter 1. 머신러닝이란: 규칙을 짜지 않고 데이터로 배우기 · 1.6 숫자를 맞히는 이웃: 회귀 · manuscript-vol2/chapters/01-what-is-ml.md:613]
import numpy as np
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor

X, y = load_diabetes(return_X_y=True)
X_학습, X_테스트, y_학습, y_테스트 = train_test_split(X, y, test_size=0.25, random_state=0)

# 비교 기준: 누구에게나 학습 데이터의 평균을 답한다
평균_답 = np.full(len(y_테스트), y_학습.mean())
print(f"평균으로 답하기: 평균 오차 {np.abs(평균_답 - y_테스트).mean():.1f}")

# 최근접 이웃 회귀: 가까운 k명의 레이블 평균을 답한다
for k in [1, 10, 30]:
    예측 = KNeighborsRegressor(n_neighbors=k).fit(X_학습, y_학습).predict(X_테스트)
    print(f"이웃 {k:2d}명의 평균: 평균 오차 {np.abs(예측 - y_테스트).mean():.1f}")
print("테스트 환자 셋의 정답:", y_테스트[:3], " k=30 예측:", 예측[:3].round(1))
