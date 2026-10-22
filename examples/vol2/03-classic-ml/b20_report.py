# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.7 분류 모델 평가하기: 정확도만 보면 속는 이유 · manuscript-vol2/chapters/03-classic-ml.md:831]
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)
y = 1 - y                                # 1 = 악성
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42)
모델 = make_pipeline(StandardScaler(), LogisticRegression()).fit(X_학습, y_학습)

print(classification_report(y_시험, 모델.predict(X_시험),
                            target_names=["benign(0)", "malignant(1)"], digits=3))
