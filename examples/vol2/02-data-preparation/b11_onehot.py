# [2권 Chapter 2. 데이터 준비: 모델에 넣기 전에 할 일 · 2.5 범주형 인코딩: 글자를 숫자로 · manuscript-vol2/chapters/02-data-preparation.md:512]
import pandas as pd
from sklearn.preprocessing import OneHotEncoder

학습 = pd.DataFrame({"지역": ["서울", "부산", "대구", "서울", "부산"]})
시험 = pd.DataFrame({"지역": ["부산", "광주"]})      # 광주는 학습 때 못 본 값

인코더 = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
인코더.fit(학습)
print("배운 범주:", 인코더.categories_[0].tolist())
print("새 열 이름:", 인코더.get_feature_names_out().tolist())
print(인코더.transform(학습))
print("시험 데이터:")
print(인코더.transform(시험))
