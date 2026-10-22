# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.7 분류 모델 평가하기: 정확도만 보면 속는 이유 · manuscript-vol2/chapters/03-classic-ml.md:740]
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)
y = 1 - y                                # 1 = 악성
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42)
모델 = make_pipeline(StandardScaler(), LogisticRegression()).fit(X_학습, y_학습)
악성_확률 = 모델.predict_proba(X_시험)[:, 1]

print("문턱   FP   FN   정밀도   재현율")
for 문턱 in [0.9, 0.5, 0.2, 0.05]:
    예측 = (악성_확률 >= 문턱).astype(int)  # 문턱을 넘으면 양성 판정
    tn, fp, fn, tp = confusion_matrix(y_시험, 예측).ravel()
    print(f"{문턱:>4} {fp:>4} {fn:>4} {tp / (tp + fp):>8.3f} {tp / (tp + fn):>8.3f}")
