# [2권 Chapter 2. 데이터 준비: 모델에 넣기 전에 할 일 · 2.8 불균형 데이터 · manuscript-vol2/chapters/02-data-preparation.md:914]
import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# 양성이 5%뿐인 분류 문제 (예제용 합성 데이터)
X, y = make_classification(n_samples=4000, n_features=8, n_informative=4,
                           weights=[0.95], flip_y=0.01, class_sep=1.5, random_state=0)
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    X, y, test_size=0.25, random_state=0, stratify=y)
print(f"시험 데이터 {len(y_시험)}건 중 양성 {y_시험.sum()}건")

for 가중치 in [None, "balanced"]:
    예측 = LogisticRegression(class_weight=가중치).fit(X_학습, y_학습).predict(X_시험)
    찾음 = ((예측 == 1) & (y_시험 == 1)).sum()
    헛경보 = ((예측 == 1) & (y_시험 == 0)).sum()
    print(f"class_weight={가중치!s:<8}  정확도 {(예측 == y_시험).mean():.1%}  "
          f"양성 {찾음}건 찾음, 헛경보 {헛경보}건")
