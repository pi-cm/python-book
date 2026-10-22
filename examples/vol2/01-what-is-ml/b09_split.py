# [2권 Chapter 1. 머신러닝이란: 규칙을 짜지 않고 데이터로 배우기 · 1.5 첫 모델: 최근접 이웃 분류 · manuscript-vol2/chapters/01-what-is-ml.md:415]
import numpy as np
from sklearn.datasets import load_iris

X, y = load_iris(return_X_y=True)

rng = np.random.default_rng(42)
섞은_번호 = rng.permutation(len(X))    # 0~149를 무작위 순서로
테스트_번호 = 섞은_번호[:30]           # 30송이는 시험용으로 숨겨 두고
학습_번호 = 섞은_번호[30:]             # 나머지 120송이로 배운다

X_학습, y_학습 = X[학습_번호], y[학습_번호]
X_테스트, y_테스트 = X[테스트_번호], y[테스트_번호]
print("학습:", X_학습.shape, "품종별", np.bincount(y_학습))
print("테스트:", X_테스트.shape, "품종별", np.bincount(y_테스트))
