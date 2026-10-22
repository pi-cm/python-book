# [2권 Chapter 2. 데이터 준비: 모델에 넣기 전에 할 일 · 2.7 ColumnTransformer와 Pipeline으로 묶기 · manuscript-vol2/chapters/02-data-preparation.md:748]
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

# 아파트 매물 (예제용으로 만든 데이터)
매물 = pd.DataFrame({
    "면적": [84.9, 59.8, np.nan, 114.5, 84.9, 49.5],
    "층": [12, 3, 25, 7, np.nan, 15],
    "구": ["마포", "강서", "마포", np.nan, "송파", "강서"],
    "상태": ["보통", "좋음", "나쁨", "좋음", "보통", np.nan],
})

숫자_열 = ["면적", "층"]
범주_열 = ["구"]
순서_열 = ["상태"]

숫자_처리 = make_pipeline(SimpleImputer(strategy="median"), StandardScaler())
범주_처리 = make_pipeline(SimpleImputer(strategy="constant", fill_value="모름"),
                          OneHotEncoder(handle_unknown="ignore", sparse_output=False))
순서_처리 = make_pipeline(SimpleImputer(strategy="most_frequent"),
                          OrdinalEncoder(categories=[["나쁨", "보통", "좋음"]]))

전처리 = ColumnTransformer([
    ("숫자", 숫자_처리, 숫자_열),
    ("범주", 범주_처리, 범주_열),
    ("순서", 순서_처리, 순서_열),
])
전처리.set_output(transform="pandas")
결과 = 전처리.fit_transform(매물)
print(결과.round(2).to_string())
