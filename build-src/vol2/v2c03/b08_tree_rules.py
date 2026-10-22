from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text

암 = load_breast_cancer()
X, y = 암.data, 1 - 암.target            # 1 = 악성
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42)

나무 = DecisionTreeClassifier(max_depth=2, random_state=42)
나무.fit(X_학습, y_학습)
print(export_text(나무, feature_names=암.feature_names.tolist(), show_weights=True))
print(f"질문 두 번만으로 시험 정확도 {나무.score(X_시험, y_시험):.3f}")
