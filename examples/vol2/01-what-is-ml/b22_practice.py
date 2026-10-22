# [2권 Chapter 1. 머신러닝이란: 규칙을 짜지 않고 데이터로 배우기 · 1.13 실습: 와인 생산자 맞히기 · manuscript-vol2/chapters/01-what-is-ml.md:1135]
import numpy as np
from sklearn.datasets import load_wine
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler


def 최근접_이웃_예측(X_학습: np.ndarray, y_학습: np.ndarray,
                    X_새: np.ndarray, k: int) -> np.ndarray:
    """새 샘플마다 가장 가까운 학습 샘플 k개의 다수결로 레이블을 정한다."""
    거리 = np.sqrt(((X_새[:, None, :] - X_학습[None, :, :]) ** 2).sum(axis=2))
    이웃 = np.argsort(거리, axis=1, kind="stable")[:, :k]
    return np.array([np.bincount(줄).argmax() for 줄 in y_학습[이웃]])


# 1) 데이터: 와인 178병 × 화학 성분 13가지, 레이블은 생산자 3곳
와인 = load_wine()
X, y = 와인.data, 와인.target
print("모양:", X.shape, " 생산자별:", np.bincount(y))
print("특성별 범위 예:", 와인.feature_names[12], X[:, 12].min(), "~", X[:, 12].max(),
      "/", 와인.feature_names[7], X[:, 7].min(), "~", X[:, 7].max())

# 2) 나누기: 학습 60%, 검증 20%, 테스트 20%
번호 = np.random.default_rng(7).permutation(len(X))
학습, 검증, 테스트 = 번호[:106], 번호[106:142], 번호[142:]

# 3) 표준화: 평균과 표준편차는 학습 데이터에서만 구한다
평균, 표준편차 = X[학습].mean(axis=0), X[학습].std(axis=0)
X_표준 = (X - 평균) / 표준편차

# 4) 검증 데이터로 설정 고르기: 표준화 여부 × k
결과 = {}
for 이름, 데이터 in [("그대로", X), ("표준화", X_표준)]:
    for k in [1, 3, 5, 9, 15]:
        예측 = 최근접_이웃_예측(데이터[학습], y[학습], 데이터[검증], k)
        결과[(이름, k)] = (예측 == y[검증]).mean()
    print(이름, " ".join(f"k={k}:{결과[(이름, k)]:.3f}" for k in [1, 3, 5, 9, 15]))
# 검증 정확도가 같으면 k가 큰 쪽(덜 외우는 쪽)을 고른다
최고_이름, 최고_k = max(결과, key=lambda 설정: (결과[설정], 설정[1]))
print(f"고른 설정: {최고_이름}, k={최고_k}")

# 5) 테스트는 마지막에 딱 한 번
데이터 = X_표준 if 최고_이름 == "표준화" else X
예측 = 최근접_이웃_예측(데이터[학습], y[학습], 데이터[테스트], 최고_k)
print(f"테스트 정확도: {(예측 == y[테스트]).mean():.3f} ({(예측 == y[테스트]).sum()}/{len(테스트)})")

# 6) scikit-learn으로 같은 결과가 나오는지 확인
척도 = StandardScaler().fit(X[학습])
모델 = KNeighborsClassifier(n_neighbors=최고_k).fit(척도.transform(X[학습]), y[학습])
print("scikit-learn과 예측이 같은가:",
      np.array_equal(모델.predict(척도.transform(X[테스트])), 예측))
