# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.13 실습: 캘리포니아 집값 예측 모델 고르기 · manuscript-vol2/chapters/03-classic-ml.md:1327]
import os

from scipy.stats import loguniform, randint
from sklearn.datasets import fetch_california_housing
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import KFold, RandomizedSearchCV, train_test_split

X, y = fetch_california_housing(data_home=os.environ.get("BOOK_DATA_DIR", "data"),
                                return_X_y=True, as_frame=True)
X_학습, X_시험, y_학습, y_시험 = train_test_split(X, y, test_size=0.2, random_state=42)

분포 = {
    "learning_rate": loguniform(0.03, 0.3),
    "max_iter": randint(100, 500),           # 나무 수
    "max_leaf_nodes": randint(15, 63),
    "min_samples_leaf": randint(10, 60),
    "l2_regularization": loguniform(1e-3, 10),
}
탐색 = RandomizedSearchCV(HistGradientBoostingRegressor(random_state=0), 분포, n_iter=8,
                          scoring="neg_root_mean_squared_error", random_state=0,
                          cv=KFold(n_splits=5, shuffle=True, random_state=0))
탐색.fit(X_학습, y_학습)

for 이름, 값 in sorted(탐색.best_params_.items()):
    print(f"{이름}: {round(값, 4)}")
print(f"교차 검증 RMSE: {-탐색.best_score_:.3f}  (기본 설정은 0.471)")
