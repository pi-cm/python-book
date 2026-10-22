# [2권 Chapter 2. 데이터 준비: 모델에 넣기 전에 할 일 · 2.9 시간 순서가 있는 데이터 · manuscript-vol2/chapters/02-data-preparation.md:955]
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor

rng = np.random.default_rng(0)
# 2년 동안 하루 판매량: 꾸준히 늘고 주말에 많이 팔린다 (예제용)
날짜 = pd.date_range("2024-01-01", "2025-12-31", freq="D")
일차 = np.arange(len(날짜))
판매 = 200 + 0.4 * 일차 + 60 * (날짜.dayofweek >= 5) + rng.normal(0, 15, len(날짜))
X = pd.DataFrame({"일차": 일차, "요일": 날짜.dayofweek})


def 평균_오차(학습_위치, 시험_위치) -> float:
    """나무 모델을 학습하고 시험 구간의 평균 절대 오차를 돌려준다."""
    모델 = DecisionTreeRegressor(min_samples_leaf=5, random_state=0)
    모델.fit(X.iloc[학습_위치], 판매[학습_위치])
    return np.abs(모델.predict(X.iloc[시험_위치]) - 판매[시험_위치]).mean()


섞은_학습, 섞은_시험 = train_test_split(일차, test_size=0.2, random_state=0)
print(f"마구 섞어 나누기: 평균 {평균_오차(섞은_학습, 섞은_시험):5.1f}개 틀림")

경계 = int(len(일차) * 0.8)                       # 앞 80%로 배우고 뒤 20%로 시험
print(f"시간 순서로 자르기: 평균 {평균_오차(일차[:경계], 일차[경계:]):5.1f}개 틀림")
print("시험 구간:", 날짜[경계].date(), "~", 날짜[-1].date())
