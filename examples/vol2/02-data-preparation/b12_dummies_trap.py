# [2권 Chapter 2. 데이터 준비: 모델에 넣기 전에 할 일 · 2.5 범주형 인코딩: 글자를 숫자로 · manuscript-vol2/chapters/02-data-preparation.md:551]
import pandas as pd

학습 = pd.DataFrame({"지역": ["서울", "부산", "대구", "서울"]})
시험 = pd.DataFrame({"지역": ["부산", "광주"]})

print("학습:", pd.get_dummies(학습).columns.tolist())
print("시험:", pd.get_dummies(시험).columns.tolist())
