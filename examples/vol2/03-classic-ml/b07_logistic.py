# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.3 로지스틱 회귀: 확률로 답하는 분류 · manuscript-vol2/chapters/03-classic-ml.md:262]
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

암 = load_breast_cancer()
X, y = 암.data, 1 - 암.target            # 1 = 악성
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42)

모델 = make_pipeline(StandardScaler(), LogisticRegression())
모델.fit(X_학습, y_학습)

확률 = 모델.predict_proba(X_시험[:5])     # 열 0: 악성 아님, 열 1: 악성
print("예측 확률:\n", 확률.round(3))
print("예측 레이블:", 모델.predict(X_시험[:5]))
print("실제 레이블:", y_시험[:5])

계수 = 모델[-1].coef_[0]                  # 특성 30개에 하나씩
for i in 계수.argsort()[::-1][:3]:       # 큰 것부터 세 개
    print(f"{암.feature_names[i]:>15}: {계수[i]:+.2f}")
