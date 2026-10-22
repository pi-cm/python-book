# [2권 Chapter 2. 데이터 준비: 모델에 넣기 전에 할 일 · 2.4 결측치 처리 · manuscript-vol2/chapters/02-data-preparation.md:464]
import numpy as np
import pandas as pd

rng = np.random.default_rng(3)
n = 2000
# 대출 신청 기록 (예제용): 형편이 어려운 사람일수록 소득 칸을 비워 두는 경향이 있다고 하자
형편 = rng.normal(size=n)
연체 = (rng.random(n) < 1 / (1 + np.exp(2 + 1.2 * 형편))).astype(int)
연소득 = np.where(rng.random(n) < 1 / (1 + np.exp(1.5 + 1.5 * 형편)), np.nan,
                 (4000 + 1200 * 형편).round())
신청 = pd.DataFrame({"연소득": 연소득, "연체": 연체})

비움 = 신청["연소득"].isna()
print(f"소득 칸을 비운 비율: {비움.mean():.1%}")
print(f"소득을 적은 사람의 연체율: {신청.loc[~비움, '연체'].mean():.1%}")
print(f"소득을 비운 사람의 연체율: {신청.loc[비움, '연체'].mean():.1%}")
