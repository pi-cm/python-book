# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.6 정답 없이 묶기: k-means 군집 · manuscript-vol2/chapters/03-classic-ml.md:616]
from sklearn.cluster import KMeans
from sklearn.datasets import load_wine
from sklearn.metrics import adjusted_rand_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

와인 = load_wine()
X, 품종 = 와인.data, 와인.target          # 품종은 채점할 때만 쓴다
print("특성 범위 예:", 와인.feature_names[12], X[:, 12].min(), "~", X[:, 12].max(),
      "/", 와인.feature_names[7], X[:, 7].min(), "~", X[:, 7].max())

그대로 = KMeans(n_clusters=3, n_init=10, random_state=0).fit_predict(X)
맞춘_뒤 = make_pipeline(StandardScaler(),
                        KMeans(n_clusters=3, n_init=10, random_state=0)).fit_predict(X)
print(f"스케일링 없이: 품종과 일치도 {adjusted_rand_score(품종, 그대로):.3f}")
print(f"스케일링 후:   품종과 일치도 {adjusted_rand_score(품종, 맞춘_뒤):.3f}")
