# [2권 Chapter 2. 데이터 준비: 모델에 넣기 전에 할 일 · 2.6 스케일링: 단위 맞추기 · manuscript-vol2/chapters/02-data-preparation.md:679]
import numpy as np
from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler

# 하루 방문자 수 (예제용). 마지막 날만 방송을 타서 크게 튀었다
방문자 = np.array([[120.0], [135.0], [128.0], [142.0], [131.0], [1500.0]])

for 스케일러 in [StandardScaler(), MinMaxScaler(), RobustScaler()]:
    결과 = 스케일러.fit_transform(방문자).ravel()
    print(f"{type(스케일러).__name__:<15}", np.round(결과, 2))
