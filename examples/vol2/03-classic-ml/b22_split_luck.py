# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.9 교차 검증: 모의고사는 한 번보다 다섯 번 · manuscript-vol2/chapters/03-classic-ml.md:923]
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)
점수들 = []
for 씨앗 in range(10):                  # 나누는 방법만 바꿔 열 번
    X_학습, X_시험, y_학습, y_시험 = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=씨앗)
    나무 = DecisionTreeClassifier(max_depth=3, random_state=0).fit(X_학습, y_학습)
    점수들.append(나무.score(X_시험, y_시험))
print("시험 정확도:", [round(s, 3) for s in 점수들])
print(f"가장 낮을 때 {min(점수들):.3f}, 가장 높을 때 {max(점수들):.3f}")
