# [2권 Chapter 2. 데이터 준비: 모델에 넣기 전에 할 일 · 2.9 시간 순서가 있는 데이터 · manuscript-vol2/chapters/02-data-preparation.md:1000]
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit

달 = pd.period_range("2025-01", "2025-12", freq="M")

for 회차, (학습, 시험) in enumerate(TimeSeriesSplit(n_splits=4).split(달), start=1):
    print(f"{회차}회차  학습 {달[학습[0]]}~{달[학습[-1]]}  →  시험 {달[시험[0]]}~{달[시험[-1]]}")
