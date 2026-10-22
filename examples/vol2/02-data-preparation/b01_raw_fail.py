# [2권 Chapter 2. 데이터 준비: 모델에 넣기 전에 할 일 · 들어가며: 장 봐 온 재료를 바로 냄비에 넣나요? · manuscript-vol2/chapters/02-data-preparation.md:19]
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

# 고객 다섯 명의 기록 (예제용으로 만든 데이터)
고객 = pd.DataFrame({
    "나이": [34, 52, np.nan, 41, 29],
    "지역": ["서울", "부산", "서울", "대구", "부산"],
    "월요금": [55000, 89000, 32000, np.nan, 45000],
    "이탈": [0, 1, 0, 1, 0],
})
X = 고객.drop(columns="이탈")     # 문제(특성)
y = 고객["이탈"]                  # 정답(레이블)

모델 = LogisticRegression()
try:
    모델.fit(X, y)                 # 그대로 넣어 보면?
except ValueError as e:
    print("오류 1:", str(e).splitlines()[0])

try:
    모델.fit(X[["나이", "월요금"]], y)   # 글자 열을 빼고 숫자만 넣어 보면?
except ValueError as e:
    print("오류 2:", str(e).splitlines()[0])
