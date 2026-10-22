# [2권 Chapter 1. 머신러닝이란: 규칙을 짜지 않고 데이터로 배우기 · 1.7 일반화와 과적합: 외우기와 이해하기 · manuscript-vol2/chapters/01-what-is-ml.md:695]
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

# 초승달 두 개가 맞물린 모양의 점들 (예제용으로 만든 데이터), 잡음을 섞었다
X, y = make_moons(n_samples=400, noise=0.35, random_state=0)
X_학습, X_테스트, y_학습, y_테스트 = train_test_split(
    X, y, test_size=0.5, random_state=0)

print("  k   학습 정확도   테스트 정확도")
for k in [1, 3, 7, 15, 31, 75, 199]:
    모델 = KNeighborsClassifier(n_neighbors=k).fit(X_학습, y_학습)
    print(f"{k:3d}      {모델.score(X_학습, y_학습):.3f}         {모델.score(X_테스트, y_테스트):.3f}")
