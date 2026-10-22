# [2권 Chapter 2. 데이터 준비: 모델에 넣기 전에 할 일 · 2.6 스케일링: 단위 맞추기 · manuscript-vol2/chapters/02-data-preparation.md:708]
import numpy as np
from sklearn.preprocessing import MinMaxScaler

학습 = np.array([[20.0], [35.0], [50.0], [65.0]])     # 학습 데이터의 나이
시험 = np.array([[30.0], [80.0]])                     # 시험 데이터의 나이

스케일러 = MinMaxScaler().fit(학습)                    # 최솟값 20, 최댓값 65를 배운다
print("배운 범위:", 스케일러.data_min_, "~", 스케일러.data_max_)
print("학습:", 스케일러.transform(학습).ravel().round(3))
print("시험:", 스케일러.transform(시험).ravel().round(3))

잘못 = MinMaxScaler().fit(np.vstack([학습, 시험]))     # 시험 데이터까지 보고 배우면
print("잘못 배운 범위:", 잘못.data_min_, "~", 잘못.data_max_)
print("학습:", 잘못.transform(학습).ravel().round(3))
