# [2권 Chapter 1. 머신러닝이란: 규칙을 짜지 않고 데이터로 배우기 · 1.10 머신러닝 작업의 흐름 · manuscript-vol2/chapters/01-what-is-ml.md:949]
from dataclasses import dataclass

import numpy as np
from sklearn.datasets import load_iris
from sklearn.neighbors import KNeighborsClassifier

붓꽃 = load_iris()
모델 = KNeighborsClassifier(n_neighbors=5).fit(붓꽃.data, 붓꽃.target)
학습_최소, 학습_최대 = 붓꽃.data.min(axis=0), 붓꽃.data.max(axis=0)


@dataclass
class 측정값:
    꽃받침_길이: float
    꽃받침_너비: float
    꽃잎_길이: float
    꽃잎_너비: float


def 품종_알려주기(측정: 측정값) -> str:
    """서비스 창구: 측정값을 받아 품종 이름을 돌려준다."""
    값 = np.array([[측정.꽃받침_길이, 측정.꽃받침_너비, 측정.꽃잎_길이, 측정.꽃잎_너비]])
    if ((값 < 학습_최소 * 0.5) | (값 > 학습_최대 * 1.5)).any():
        return "모르겠어요 (배운 적 없는 크기)"
    return str(붓꽃.target_names[모델.predict(값)[0]])


print("모델에 바로 묻기:", 붓꽃.target_names[모델.predict([[5.0, 3.4, 100.0, 0.2]])[0]])
print("창구로 묻기 1:", 품종_알려주기(측정값(5.0, 3.4, 1.5, 0.2)))
print("창구로 묻기 2:", 품종_알려주기(측정값(5.0, 3.4, 100.0, 0.2)))
