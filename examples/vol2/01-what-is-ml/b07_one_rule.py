# [2권 Chapter 1. 머신러닝이란: 규칙을 짜지 않고 데이터로 배우기 · 1.4 모델, 학습, 예측 · manuscript-vol2/chapters/01-what-is-ml.md:322]
import numpy as np
from sklearn.datasets import load_iris

X, y = load_iris(return_X_y=True)
고름 = y > 0                       # versicolor(1)와 virginica(2)만
꽃잎_길이 = X[고름, 2]             # 특성 하나: 꽃잎 길이(cm)
정답 = y[고름]

최고_기준, 최고_정확도 = None, 0.0
for 기준 in np.unique(꽃잎_길이):                  # 후보 기준을 하나씩 시험
    예측 = np.where(꽃잎_길이 > 기준, 2, 1)         # 기준보다 길면 virginica
    정확도 = (예측 == 정답).mean()
    if 정확도 > 최고_정확도:
        최고_기준, 최고_정확도 = 기준, 정확도

print("시험한 기준 수:", len(np.unique(꽃잎_길이)))
print(f"배운 규칙: 꽃잎 길이 > {최고_기준} 이면 virginica")
print(f"학습 데이터에서 정확도: {최고_정확도:.2f}")
