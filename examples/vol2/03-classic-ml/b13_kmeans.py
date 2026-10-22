# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.6 정답 없이 묶기: k-means 군집 · manuscript-vol2/chapters/03-classic-ml.md:551]
import numpy as np
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs

# 예제용으로 만든 데이터: 정답 레이블 없이 점 300개만 있다고 하자
X, _ = make_blobs(n_samples=300, centers=3, cluster_std=1.0, random_state=7)

군집 = KMeans(n_clusters=3, n_init=10, random_state=0)
번호 = 군집.fit_predict(X)              # 배우고 곧바로 각 점의 무리 번호 받기
print("처음 10개 점의 무리 번호:", 번호[:10])
print("무리별 점 개수:", np.bincount(번호))
print("무리 중심:\n", 군집.cluster_centers_.round(2))
print("새 점 두 개의 무리:", 군집.predict([[9.0, 1.0], [-8.0, 5.0]]))
