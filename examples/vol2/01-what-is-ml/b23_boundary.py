# [2권 Chapter 1. 머신러닝이란: 규칙을 짜지 않고 데이터로 배우기 · 1.7 일반화와 과적합: 외우기와 이해하기 · manuscript-vol2/chapters/01-what-is-ml.md:739]
import numpy as np
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

X, y = make_moons(n_samples=400, noise=0.35, random_state=0)   # 예제용 데이터
X_학습, X_테스트, y_학습, y_테스트 = train_test_split(
    X, y, test_size=0.5, random_state=0)

# 평면을 가로 48칸 × 세로 14칸 격자로 나누고, 칸마다 모델의 답을 찍는다
가로 = np.linspace(-1.6, 2.6, 48)
세로 = np.linspace(1.6, -1.0, 14)
격자 = np.array([[x, 높이] for 높이 in 세로 for x in 가로])

for k in [1, 31]:
    모델 = KNeighborsClassifier(n_neighbors=k).fit(X_학습, y_학습)
    지도 = 모델.predict(격자).reshape(len(세로), len(가로))
    print(f"[k={k}]  # = 0번 달, . = 1번 달")
    for 줄 in 지도:
        print("".join("#" if 값 == 0 else "." for 값 in 줄))
