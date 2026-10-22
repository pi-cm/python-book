# [2권 Chapter 2. 데이터 준비: 모델에 넣기 전에 할 일 · 2.7 ColumnTransformer와 Pipeline으로 묶기 · manuscript-vol2/chapters/02-data-preparation.md:808]
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

rng = np.random.default_rng(0)
n = 400
# 헬스장 회원 (예제용): 방문이 뜸하고 나이가 많을수록 재등록을 안 한다고 하자
회원 = pd.DataFrame({
    "나이": rng.integers(20, 65, n).astype(float),
    "주간방문": rng.poisson(2.5, n).astype(float),
    "지점": rng.choice(["강남", "홍대", "잠실"], n),
})
확률 = 1 / (1 + np.exp(-(1.0 - 0.04 * (회원["나이"] - 40) + 0.6 * (회원["주간방문"] - 2.5))))
회원["재등록"] = (rng.random(n) < 확률).astype(int)
회원.loc[rng.random(n) < 0.1, "나이"] = np.nan          # 일부는 나이를 안 적었다

X, y = 회원.drop(columns="재등록"), 회원["재등록"]
X_학습, X_시험, y_학습, y_시험 = train_test_split(X, y, test_size=0.25, random_state=0)

전처리 = ColumnTransformer([
    ("숫자", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()),
     ["나이", "주간방문"]),
    ("범주", OneHotEncoder(handle_unknown="ignore"), ["지점"]),
])
모델 = Pipeline([("전처리", 전처리), ("분류", LogisticRegression())])

모델.fit(X_학습, y_학습)            # 전처리도 모델도 학습 데이터로만 배운다
print(f"시험 정확도: {모델.score(X_시험, y_시험):.1%}")

새_회원 = pd.DataFrame({"나이": [np.nan, 58.0], "주간방문": [4.0, 0.0], "지점": ["판교", "강남"]})
print("새 회원 재등록 확률:", 모델.predict_proba(새_회원)[:, 1].round(2))
print("배운 중앙값:", 모델.named_steps["전처리"].named_transformers_["숫자"][0].statistics_)
