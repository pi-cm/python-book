# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.5 여럿이 함께: 랜덤 포레스트와 그래디언트 부스팅 · manuscript-vol2/chapters/03-classic-ml.md:395]
from sklearn.datasets import make_moons
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

# 3.4절과 같은 예제용 두 반달 데이터
X, y = make_moons(n_samples=400, noise=0.35, random_state=0)
X_학습, X_시험, y_학습, y_시험 = train_test_split(X, y, test_size=0.3, random_state=0)

나무 = DecisionTreeClassifier(random_state=0).fit(X_학습, y_학습)
print(f"끝까지 자란 나무 한 그루: 시험 정확도 {나무.score(X_시험, y_시험):.3f}")
for 그루_수 in [1, 10, 50, 200]:
    숲 = RandomForestClassifier(n_estimators=그루_수, random_state=0).fit(X_학습, y_학습)
    print(f"나무 {그루_수:>3}그루짜리 숲: 학습 {숲.score(X_학습, y_학습):.3f},"
          f" 시험 {숲.score(X_시험, y_시험):.3f}")
