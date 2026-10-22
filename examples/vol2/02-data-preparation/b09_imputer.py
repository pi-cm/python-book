# [2권 Chapter 2. 데이터 준비: 모델에 넣기 전에 할 일 · 2.4 결측치 처리 · manuscript-vol2/chapters/02-data-preparation.md:411]
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer

# 연소득(만 원). 학습 데이터에 아주 큰 값이 하나 섞여 있다 (예제용)
학습 = pd.DataFrame({"연소득": [3200, 4100, np.nan, 3800, 4500, 250000, np.nan, 3600]})
시험 = pd.DataFrame({"연소득": [np.nan, 5000]})

평균_채우기 = SimpleImputer(strategy="mean").fit(학습)
중앙값_채우기 = SimpleImputer(strategy="median").fit(학습)
print("학습 데이터로 배운 평균:", 평균_채우기.statistics_.round(1))
print("학습 데이터로 배운 중앙값:", 중앙값_채우기.statistics_)
print("시험 데이터 채우기(중앙값):", 중앙값_채우기.transform(시험).ravel())

# 비어 있었다는 사실도 함께 남기기
표시 = SimpleImputer(strategy="median", add_indicator=True)
표시.set_output(transform="pandas")          # 결과를 DataFrame으로 받기
print(표시.fit(학습).transform(시험))

# 글자 열: 가장 흔한 값 또는 정해 둔 값으로
지역 = pd.DataFrame({"지역": ["서울", "부산", np.nan, "서울", "대구"]})
print(SimpleImputer(strategy="most_frequent").fit_transform(지역).ravel())
print(SimpleImputer(strategy="constant", fill_value="모름").fit_transform(지역).ravel())
