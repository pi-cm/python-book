# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.7 분류 모델 평가하기: 정확도만 보면 속는 이유 · manuscript-vol2/chapters/03-classic-ml.md:651]
import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, recall_score

# 예제용으로 만든 데이터: 1,000명 중 10명(1%)만 감염자(1)
rng = np.random.default_rng(0)
y = np.zeros(1000, dtype=int)
y[rng.choice(1000, size=10, replace=False)] = 1
X = rng.normal(size=(1000, 3))          # 의미 없는 특성 (게으른 검사기는 보지도 않는다)

게으른_검사기 = DummyClassifier(strategy="most_frequent").fit(X, y)
예측 = 게으른_검사기.predict(X)          # 누구에게나 "음성"
print("양성 판정 수:", 예측.sum())
print(f"정확도: {accuracy_score(y, 예측):.3f}")
print(f"감염자 중 찾아낸 비율(재현율): {recall_score(y, 예측):.3f}")
