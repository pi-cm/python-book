# [2권 Chapter 1. 머신러닝이란: 규칙을 짜지 않고 데이터로 배우기 · 1.5 첫 모델: 최근접 이웃 분류 · manuscript-vol2/chapters/01-what-is-ml.md:529]
import numpy as np
from sklearn.datasets import load_iris
from sklearn.neighbors import KNeighborsClassifier

붓꽃 = load_iris()
모델 = KNeighborsClassifier(n_neighbors=5).fit(붓꽃.data, 붓꽃.target)

새_꽃들 = np.array([[5.0, 3.4, 1.5, 0.2],    # 예제용으로 지어낸 꽃 세 송이
                    [6.0, 2.9, 4.6, 1.5],
                    [6.3, 2.8, 5.0, 1.7]])
확률 = 모델.predict_proba(새_꽃들)            # 이웃 다섯 중 품종별 비율
for 꽃, 줄 in zip(새_꽃들, 확률):
    이름 = 붓꽃.target_names[줄.argmax()]
    print(f"{꽃} → {줄.round(2)}  {이름}")
