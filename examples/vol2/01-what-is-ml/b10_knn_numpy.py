# [2권 Chapter 1. 머신러닝이란: 규칙을 짜지 않고 데이터로 배우기 · 1.5 첫 모델: 최근접 이웃 분류 · manuscript-vol2/chapters/01-what-is-ml.md:445]
import numpy as np
from sklearn.datasets import load_iris


def 최근접_이웃_예측(X_학습: np.ndarray, y_학습: np.ndarray,
                    X_새: np.ndarray, k: int) -> np.ndarray:
    """새 샘플마다 가장 가까운 학습 샘플 k개의 다수결로 레이블을 정한다."""
    # (새 개수, 1, 특성) - (1, 학습 개수, 특성) → (새 개수, 학습 개수, 특성)
    차이 = X_새[:, np.newaxis, :] - X_학습[np.newaxis, :, :]
    거리 = np.sqrt((차이 ** 2).sum(axis=2))           # (새 개수, 학습 개수)
    이웃 = np.argsort(거리, axis=1, kind="stable")[:, :k]  # 가까운 k개의 번호
    이웃_레이블 = y_학습[이웃]                         # (새 개수, k)
    return np.array([np.bincount(줄).argmax() for 줄 in 이웃_레이블])


X, y = load_iris(return_X_y=True)
섞은_번호 = np.random.default_rng(42).permutation(len(X))
X_학습, y_학습 = X[섞은_번호[30:]], y[섞은_번호[30:]]
X_테스트, y_테스트 = X[섞은_번호[:30]], y[섞은_번호[:30]]

예측 = 최근접_이웃_예측(X_학습, y_학습, X_테스트, k=5)
print("예측:", 예측[:10])
print("정답:", y_테스트[:10])
print(f"테스트 정확도: {(예측 == y_테스트).mean():.3f} ({(예측 == y_테스트).sum()}/{len(y_테스트)})")
