# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.13 실습: 캘리포니아 집값 예측 모델 고르기 · manuscript-vol2/chapters/03-classic-ml.md:1371]
import os
from pathlib import Path

import joblib
import sklearn
from sklearn.datasets import fetch_california_housing
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import train_test_split

X, y = fetch_california_housing(data_home=os.environ.get("BOOK_DATA_DIR", "data"),
                                return_X_y=True, as_frame=True)
X_학습, X_시험, y_학습, y_시험 = train_test_split(X, y, test_size=0.2, random_state=42)

# 3단계에서 찾은 설정을 옮겨 적는다
최종 = HistGradientBoostingRegressor(
    learning_rate=0.0893, max_iter=470, max_leaf_nodes=43,
    min_samples_leaf=44, l2_regularization=0.0027, random_state=0)
최종.fit(X_학습, y_학습)                  # 학습 세트 전체로 학습

예측 = 최종.predict(X_시험)               # 봉인했던 시험 세트, 딱 한 번
print(f"시험 RMSE {root_mean_squared_error(y_시험, 예측):.3f}, "
      f"MAE {mean_absolute_error(y_시험, 예측):.3f}, R² {r2_score(y_시험, 예측):.3f}")

경로 = Path("models") / "california_hgb.joblib"
경로.parent.mkdir(exist_ok=True)
joblib.dump({"model": 최종, "sklearn_version": sklearn.__version__,
             "features": list(X.columns)}, 경로)

꾸러미 = joblib.load(경로)
새_구역 = X_시험.head(3)
for 예상, 실제 in zip(꾸러미["model"].predict(새_구역), y_시험.head(3)):
    print(f"예상 {예상 * 10:5.2f}만 달러 / 실제 {실제 * 10:5.2f}만 달러")
