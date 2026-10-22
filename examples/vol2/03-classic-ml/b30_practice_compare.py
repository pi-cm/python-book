# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.13 실습: 캘리포니아 집값 예측 모델 고르기 · manuscript-vol2/chapters/03-classic-ml.md:1279]
import os

from sklearn.datasets import fetch_california_housing
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, cross_validate, train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = fetch_california_housing(data_home=os.environ.get("BOOK_DATA_DIR", "data"),
                                return_X_y=True, as_frame=True)
X_학습, X_시험, y_학습, y_시험 = train_test_split(X, y, test_size=0.2, random_state=42)

후보들 = {
    "평균 찍기": DummyRegressor(),
    "선형 회귀": make_pipeline(StandardScaler(), LinearRegression()),
    "최근접 이웃": make_pipeline(StandardScaler(), KNeighborsRegressor(n_neighbors=10)),
    "랜덤 포레스트": RandomForestRegressor(n_estimators=100, min_samples_leaf=2,
                                          n_jobs=-1, random_state=0),
    "부스팅": HistGradientBoostingRegressor(random_state=0),
}
접기 = KFold(n_splits=5, shuffle=True, random_state=0)
for 이름, 모델 in 후보들.items():                  # 시험 세트는 여기서 쓰지 않는다
    결과 = cross_validate(모델, X_학습, y_학습, cv=접기,
                          scoring=["neg_root_mean_squared_error", "r2"])
    rmse = -결과["test_neg_root_mean_squared_error"]
    print(f"{이름}: RMSE {rmse.mean():.3f} ± {rmse.std():.3f}, R² {결과['test_r2'].mean():.3f}")
