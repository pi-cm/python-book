# [2권 Chapter 1. 머신러닝이란: 규칙을 짜지 않고 데이터로 배우기 · 1.7 일반화와 과적합: 외우기와 이해하기 · manuscript-vol2/chapters/01-what-is-ml.md:803]
from sklearn.datasets import make_moons
from sklearn.neighbors import KNeighborsClassifier

# 테스트용 1000개는 고정해 두고, 학습 데이터 양만 늘려 본다 (예제용 데이터)
X_테스트, y_테스트 = make_moons(n_samples=1000, noise=0.35, random_state=1)
X_전체, y_전체 = make_moons(n_samples=3000, noise=0.35, random_state=2)

print("학습 개수   k=1 테스트   k=15 테스트")
for 개수 in [20, 50, 200, 1000, 3000]:
    점수 = []
    for k in [1, 15]:
        k = min(k, 개수)
        모델 = KNeighborsClassifier(n_neighbors=k).fit(X_전체[:개수], y_전체[:개수])
        점수.append(모델.score(X_테스트, y_테스트))
    print(f"{개수:6d}       {점수[0]:.3f}        {점수[1]:.3f}")
