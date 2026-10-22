# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.8 회귀 모델 평가하기: MAE, RMSE, R² · manuscript-vol2/chapters/03-classic-ml.md:867]
import numpy as np
from sklearn.datasets import load_diabetes
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import train_test_split

X, y = load_diabetes(return_X_y=True)
X_학습, X_시험, y_학습, y_시험 = train_test_split(X, y, test_size=0.25, random_state=42)
예측 = LinearRegression().fit(X_학습, y_학습).predict(X_시험)

오차 = y_시험 - 예측
mae = np.abs(오차).mean()
rmse = np.sqrt((오차 ** 2).mean())
r2 = 1 - (오차 ** 2).sum() / ((y_시험 - y_시험.mean()) ** 2).sum()
print(f"직접 계산: MAE {mae:.1f}, RMSE {rmse:.1f}, R² {r2:.3f}")
print(f"sklearn : MAE {mean_absolute_error(y_시험, 예측):.1f}, "
      f"RMSE {root_mean_squared_error(y_시험, 예측):.1f}, R² {r2_score(y_시험, 예측):.3f}")

평균_찍기 = DummyRegressor(strategy="mean").fit(X_학습, y_학습).predict(X_시험)
print(f"평균으로 찍기: MAE {mean_absolute_error(y_시험, 평균_찍기):.1f}, "
      f"RMSE {root_mean_squared_error(y_시험, 평균_찍기):.1f}, R² {r2_score(y_시험, 평균_찍기):.3f}")

# 큰 실수 하나가 섞이면?
망친_예측 = 예측.copy()
망친_예측[0] += 300
print(f"한 명을 300 틀리면: MAE {mean_absolute_error(y_시험, 망친_예측):.1f}, "
      f"RMSE {root_mean_squared_error(y_시험, 망친_예측):.1f}")
