# [2권 Chapter 1. 머신러닝이란: 규칙을 짜지 않고 데이터로 배우기 · 1.5 첫 모델: 최근접 이웃 분류 · manuscript-vol2/chapters/01-what-is-ml.md:488]
import numpy as np
from sklearn.datasets import load_iris
from sklearn.neighbors import KNeighborsClassifier


def 최근접_이웃_예측(X_학습: np.ndarray, y_학습: np.ndarray,
                    X_새: np.ndarray, k: int) -> np.ndarray:
    """새 샘플마다 가장 가까운 학습 샘플 k개의 다수결로 레이블을 정한다."""
    거리 = np.sqrt(((X_새[:, None, :] - X_학습[None, :, :]) ** 2).sum(axis=2))
    이웃 = np.argsort(거리, axis=1, kind="stable")[:, :k]
    return np.array([np.bincount(줄).argmax() for 줄 in y_학습[이웃]])


X, y = load_iris(return_X_y=True)
섞은_번호 = np.random.default_rng(42).permutation(len(X))
X_학습, y_학습 = X[섞은_번호[30:]], y[섞은_번호[30:]]
X_테스트, y_테스트 = X[섞은_번호[:30]], y[섞은_번호[:30]]

모델 = KNeighborsClassifier(n_neighbors=5)   # 1) 모델 고르기
모델.fit(X_학습, y_학습)                     # 2) 학습
예측 = 모델.predict(X_테스트)                # 3) 예측
print(f"scikit-learn 정확도: {모델.score(X_테스트, y_테스트):.3f}")

직접 = 최근접_이웃_예측(X_학습, y_학습, X_테스트, k=5)
print("직접 짠 것과 예측이 모두 같은가:", np.array_equal(예측, 직접))
