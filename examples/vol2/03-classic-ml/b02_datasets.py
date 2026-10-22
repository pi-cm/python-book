# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.1 scikit-learn의 약속: fit, predict, score · manuscript-vol2/chapters/03-classic-ml.md:78]
import numpy as np
from sklearn.datasets import load_breast_cancer, load_diabetes

암 = load_breast_cancer()
print("유방암 진단 데이터:", 암.data.shape)
print("  특성 예:", 암.feature_names[:3].tolist())
print("  레이블 이름과 개수:", dict(zip(암.target_names.tolist(), np.bincount(암.target).tolist())))
y = 1 - 암.target                     # 0과 1을 뒤집어 1 = 악성으로
print("  뒤집은 뒤 악성(1) 개수:", y.sum())

당뇨 = load_diabetes()
print("당뇨병 진행도 데이터:", 당뇨.data.shape)
print("  특성:", list(당뇨.feature_names))
print("  목표값 범위:", 당뇨.target.min(), "~", 당뇨.target.max())
