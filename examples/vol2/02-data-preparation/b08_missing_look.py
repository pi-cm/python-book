# [2권 Chapter 2. 데이터 준비: 모델에 넣기 전에 할 일 · 2.4 결측치 처리 · manuscript-vol2/chapters/02-data-preparation.md:383]
import numpy as np
import pandas as pd

rng = np.random.default_rng(0)
n = 1000
# 열 다섯 개가 각자 10%씩 비어 있는 표 (예제용)
표 = pd.DataFrame(rng.normal(size=(n, 5)), columns=["가", "나", "다", "라", "마"])
for 열 in 표.columns:
    표.loc[rng.random(n) < 0.10, 열] = np.nan

print("열마다 빈 비율:", 표.isna().mean().round(3).tolist())
print("한 칸이라도 빈 행 비율:", round(표.isna().any(axis=1).mean(), 3))
print("dropna() 후 남은 행:", len(표.dropna()), "/", n)
