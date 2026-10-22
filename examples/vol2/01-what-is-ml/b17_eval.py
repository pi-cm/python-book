# [2권 Chapter 1. 머신러닝이란: 규칙을 짜지 않고 데이터로 배우기 · 1.9 얼마나 잘하나: 평가 맛보기 · manuscript-vol2/chapters/01-what-is-ml.md:881]
import numpy as np
from sklearn.datasets import load_iris
from sklearn.metrics import confusion_matrix
from sklearn.neighbors import KNeighborsClassifier

X, y = load_iris(return_X_y=True)
섞은_번호 = np.random.default_rng(42).permutation(len(X))
X_학습, y_학습 = X[섞은_번호[30:]], y[섞은_번호[30:]]
X_테스트, y_테스트 = X[섞은_번호[:30]], y[섞은_번호[:30]]

# 비교 기준: 학습 데이터에서 가장 많은 품종을 무조건 답하는 "모델"
가장_흔한 = np.bincount(y_학습).argmax()
print(f"늘 {가장_흔한}번이라고 답하면: {(y_테스트 == 가장_흔한).mean():.3f}")

예측 = KNeighborsClassifier(n_neighbors=5).fit(X_학습, y_학습).predict(X_테스트)
print(f"최근접 이웃(k=5):      {(예측 == y_테스트).mean():.3f}")
print("혼동 행렬 (행: 정답, 열: 예측)")
print(confusion_matrix(y_테스트, 예측))

# 정확도의 함정: 거래 1000건 중 사기가 10건뿐이라면?
사기 = np.zeros(1000, dtype=int)
사기[:10] = 1
늘_정상 = np.zeros(1000, dtype=int)
print(f"늘 '정상'이라고 답하는 모델의 정확도: {(늘_정상 == 사기).mean():.3f}, "
      f"찾아낸 사기: {((늘_정상 == 1) & (사기 == 1)).sum()}건")
