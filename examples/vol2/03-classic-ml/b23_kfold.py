# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.9 교차 검증: 모의고사는 한 번보다 다섯 번 · manuscript-vol2/chapters/03-classic-ml.md:957]
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import KFold
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)
접기 = KFold(n_splits=5, shuffle=True, random_state=0)

점수들 = []
for 번호, (학습_칸, 검증_칸) in enumerate(접기.split(X), start=1):
    나무 = DecisionTreeClassifier(max_depth=3, random_state=0)
    나무.fit(X[학습_칸], y[학습_칸])          # 네 묶음으로 배우고
    점수 = 나무.score(X[검증_칸], y[검증_칸])  # 남은 한 묶음으로 채점
    점수들.append(점수)
    print(f"{번호}번째: 학습 {len(학습_칸)}개, 검증 {len(검증_칸)}개 → 정확도 {점수:.3f}")
print(f"평균 {np.mean(점수들):.3f} ± {np.std(점수들):.3f}")
