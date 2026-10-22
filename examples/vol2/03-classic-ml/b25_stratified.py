# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.9 교차 검증: 모의고사는 한 번보다 다섯 번 · manuscript-vol2/chapters/03-classic-ml.md:1028]
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import KFold, StratifiedKFold, cross_val_score
from sklearn.tree import DecisionTreeClassifier

X, y = load_iris(return_X_y=True)
print("레이블 앞부분과 뒷부분:", y[:5], y[-5:])   # 품종 순서대로 정렬되어 있다

for 이름, 접기 in [("KFold(섞지 않음)", KFold(n_splits=3)),
                   ("StratifiedKFold", StratifiedKFold(n_splits=3))]:
    print(이름)
    for _, 검증_칸 in 접기.split(X, y):
        print("  검증 묶음의 품종별 개수:", np.bincount(y[검증_칸], minlength=3))
    점수 = cross_val_score(DecisionTreeClassifier(random_state=0), X, y, cv=접기)
    print("  정확도:", 점수.round(3))
