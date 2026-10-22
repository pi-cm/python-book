# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.13 실습: 캘리포니아 집값 예측 모델 고르기 · manuscript-vol2/chapters/03-classic-ml.md:1246]
import os

from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split

# 처음 한 번은 인터넷에서 받아 data/ 폴더에 저장하고, 다음부터는 거기서 읽는다
집 = fetch_california_housing(data_home=os.environ.get("BOOK_DATA_DIR", "data"), as_frame=True)
X, y = 집.data, 집.target                 # y: 구역의 집값 중앙값(단위 10만 달러)
print(X.shape)
print(X.head(3).round(2).to_string())
print("집값 범위:", y.min(), "~", y.max(), "/ 평균", round(y.mean(), 3))

X_학습, X_시험, y_학습, y_시험 = train_test_split(X, y, test_size=0.2, random_state=42)
print("학습:", X_학습.shape, "시험:", X_시험.shape)
