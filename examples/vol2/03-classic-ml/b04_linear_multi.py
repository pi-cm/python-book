# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.2 선형 회귀: 숫자를 예측하는 직선 · manuscript-vol2/chapters/03-classic-ml.md:150]
from sklearn.datasets import load_diabetes
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

당뇨 = load_diabetes()
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    당뇨.data, 당뇨.target, test_size=0.25, random_state=42)

모델 = make_pipeline(StandardScaler(), LinearRegression())
모델.fit(X_학습, y_학습)

선형 = 모델[-1]                        # 파이프라인의 마지막 단계 꺼내기
계수 = sorted(zip(당뇨.feature_names, 선형.coef_), key=lambda 쌍: -abs(쌍[1]))
for 이름, 값 in 계수:
    print(f"{이름:>4}: {값:+7.1f}")
print(f"절편: {선형.intercept_:.1f}")
print(f"시험 세트 R²: {모델.score(X_시험, y_시험):.3f}")
