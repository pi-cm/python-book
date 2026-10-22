# [2권 Chapter 2. 데이터 준비: 모델에 넣기 전에 할 일 · 2.2 학습·검증·테스트로 나누기 · manuscript-vol2/chapters/02-data-preparation.md:191]
import numpy as np
from sklearn.neighbors import KNeighborsClassifier

rng = np.random.default_rng(0)
# 정답이 동전 던지기로 정해진 데이터: 어떤 모델도 50%보다 잘할 수 없다
X_학습, y_학습 = rng.normal(size=(200, 10)), rng.integers(0, 2, 200)
X_시험, y_시험 = rng.normal(size=(100, 10)), rng.integers(0, 2, 100)
X_새, y_새 = rng.normal(size=(20000, 10)), rng.integers(0, 2, 20000)

기록 = []
for 번호 in range(50):                              # 후보 모델 50개
    열 = rng.choice(10, size=3, replace=False)       # 특성 3개를 골라 쓰는 모델
    k = int(rng.integers(1, 30))
    모델 = KNeighborsClassifier(n_neighbors=k).fit(X_학습[:, 열], y_학습)
    기록.append((모델.score(X_시험[:, 열], y_시험), 열, 모델))

시험점수, 열, 최고 = max(기록, key=lambda 행: 행[0])
print(f"시험지를 보며 고른 최고 모델의 시험 점수: {시험점수:.0%}")
print(f"같은 모델을 처음 보는 데이터 2만 개로 채점: {최고.score(X_새[:, 열], y_새):.1%}")
