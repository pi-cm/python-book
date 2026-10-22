# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.4 결정 트리: 스무고개로 답 찾기 · manuscript-vol2/chapters/03-classic-ml.md:355]
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

# 예제용으로 만든 데이터: 잡음 섞인 두 반달 모양의 점 400개
X, y = make_moons(n_samples=400, noise=0.35, random_state=0)
X_학습, X_시험, y_학습, y_시험 = train_test_split(X, y, test_size=0.3, random_state=0)

print("깊이  잎 수  학습 정확도  시험 정확도")
for 깊이 in [1, 2, 4, 6, 8, None]:
    나무 = DecisionTreeClassifier(max_depth=깊이, random_state=0).fit(X_학습, y_학습)
    print(f"{str(깊이):>4} {나무.get_n_leaves():>5} {나무.score(X_학습, y_학습):>12.3f}"
          f" {나무.score(X_시험, y_시험):>12.3f}")
