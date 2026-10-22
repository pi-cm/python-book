# [2권 Chapter 2. 데이터 준비: 모델에 넣기 전에 할 일 · 2.3 데이터 누수: 시험 문제가 새는 길 · manuscript-vol2/chapters/02-data-preparation.md:237]
import numpy as np
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

rng = np.random.default_rng(0)
X = rng.normal(size=(100, 5000))     # 100명 × 특성 5000개, 전부 의미 없는 난수
y = rng.integers(0, 2, size=100)     # 정답도 동전 던지기

# 잘못된 순서: 전체 데이터로 "정답과 관련 있어 보이는" 특성 20개를 고른 뒤 나눈다
골라 = SelectKBest(f_classif, k=20).fit_transform(X, y)
X_학습, X_시험, y_학습, y_시험 = train_test_split(골라, y, test_size=0.3, random_state=0)
모델 = LogisticRegression().fit(X_학습, y_학습)
print(f"누수 있음: 시험 점수 {모델.score(X_시험, y_시험):.0%}")

# 올바른 순서: 먼저 나누고, 학습 데이터만 보고 고른다
X_학습, X_시험, y_학습, y_시험 = train_test_split(X, y, test_size=0.3, random_state=0)
선택기 = SelectKBest(f_classif, k=20).fit(X_학습, y_학습)
모델 = LogisticRegression().fit(선택기.transform(X_학습), y_학습)
print(f"누수 없음: 시험 점수 {모델.score(선택기.transform(X_시험), y_시험):.0%}")
