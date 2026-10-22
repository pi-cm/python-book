from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.metrics import silhouette_score

X, _ = make_blobs(n_samples=300, centers=3, cluster_std=1.0, random_state=7)

print(" k   관성(inertia)   실루엣 점수")
for k in range(2, 7):
    군집 = KMeans(n_clusters=k, n_init=10, random_state=0).fit(X)
    print(f"{k:>2} {군집.inertia_:>14.1f} {silhouette_score(X, 군집.labels_):>13.3f}")
