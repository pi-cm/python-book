# [2권 Chapter 2. 데이터 준비: 모델에 넣기 전에 할 일 · 2.3 데이터 누수: 시험 문제가 새는 길 · manuscript-vol2/chapters/02-data-preparation.md:281]
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

rng = np.random.default_rng(1)
n = 1000
# 통신사 고객 기록 (예제용으로 만든 데이터)
고객 = pd.DataFrame({
    "가입개월": rng.integers(1, 60, n),
    "상담횟수": rng.poisson(1.5, n),
})
확률 = 1 / (1 + np.exp(-(-1.5 - 0.03 * 고객["가입개월"] + 0.5 * 고객["상담횟수"])))
고객["이탈"] = (rng.random(n) < 확률).astype(int)
# 해지할 때만 생기는 기록: 이탈한 고객에게만 위약금이 찍힌다
고객["위약금"] = np.where(고객["이탈"] == 1, rng.integers(1, 20, n) * 10000, 0)


def 점수_보기(특성: list[str]) -> float:
    """주어진 특성으로 학습하고 시험 점수를 돌려준다."""
    X_학습, X_시험, y_학습, y_시험 = train_test_split(
        고객[특성], 고객["이탈"], test_size=0.3, random_state=0)
    모델 = LogisticRegression(max_iter=1000).fit(X_학습, y_학습)
    return 모델.score(X_시험, y_시험)


print(f"가입개월·상담횟수만:  {점수_보기(['가입개월', '상담횟수']):.1%}")
print(f"위약금까지 넣으면:    {점수_보기(['가입개월', '상담횟수', '위약금']):.1%}")
print("정답과의 상관계수:")
print(고객.corr()["이탈"].drop("이탈").round(2).to_string())
