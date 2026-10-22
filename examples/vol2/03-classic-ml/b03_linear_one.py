# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.2 선형 회귀: 숫자를 예측하는 직선 · manuscript-vol2/chapters/03-classic-ml.md:118]
import numpy as np
from sklearn.linear_model import LinearRegression

# 예제용으로 만든 데이터: 집 넓이(평)와 가격(억 원)
rng = np.random.default_rng(0)
넓이 = rng.uniform(10, 40, size=50)
가격 = 1.0 + 0.15 * 넓이 + rng.normal(0, 0.3, size=50)   # 숨은 규칙 + 잡음

모델 = LinearRegression()
모델.fit(넓이.reshape(-1, 1), 가격)     # X는 언제나 (샘플 수, 특성 수) 2차원
print(f"기울기(평당 가격): {모델.coef_[0]:.3f}억 원")
print(f"절편(기본 가격):   {모델.intercept_:.3f}억 원")
print("30평, 35평 예상 가격:", 모델.predict([[30], [35]]).round(2))
