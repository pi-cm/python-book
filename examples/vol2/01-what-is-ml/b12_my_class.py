# [2권 Chapter 1. 머신러닝이란: 규칙을 짜지 않고 데이터로 배우기 · 1.5 첫 모델: 최근접 이웃 분류 · manuscript-vol2/chapters/01-what-is-ml.md:558]
import numpy as np
from sklearn.datasets import load_iris
from sklearn.neighbors import KNeighborsClassifier


class 최근접이웃분류기:
    """scikit-learn과 같은 fit/predict 모양으로 감싼 최근접 이웃 분류기."""

    def __init__(self, n_neighbors: int = 5) -> None:
        self.n_neighbors = n_neighbors

    def fit(self, X: np.ndarray, y: np.ndarray) -> "최근접이웃분류기":
        # 최근접 이웃의 "학습"은 데이터를 그대로 외워 두는 것뿐이다
        self.X_, self.y_ = X.copy(), y.copy()
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        거리 = np.sqrt(((X[:, None, :] - self.X_[None, :, :]) ** 2).sum(axis=2))
        이웃 = np.argsort(거리, axis=1, kind="stable")[:, :self.n_neighbors]
        return np.array([np.bincount(줄).argmax() for 줄 in self.y_[이웃]])

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        return float((self.predict(X) == y).mean())


X, y = load_iris(return_X_y=True)
섞은_번호 = np.random.default_rng(42).permutation(len(X))
X_학습, y_학습 = X[섞은_번호[30:]], y[섞은_번호[30:]]
X_테스트, y_테스트 = X[섞은_번호[:30]], y[섞은_번호[:30]]

# 사용법이 같으니 같은 반복문에 넣어 돌릴 수 있다
for 모델 in [최근접이웃분류기(n_neighbors=3), KNeighborsClassifier(n_neighbors=3)]:
    모델.fit(X_학습, y_학습)
    print(f"{type(모델).__name__:22s} 정확도 {모델.score(X_테스트, y_테스트):.3f}")
