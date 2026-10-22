# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.2 선형 회귀: 숫자를 예측하는 직선 · manuscript-vol2/chapters/03-classic-ml.md:195]
from sklearn.datasets import load_diabetes
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

당뇨 = load_diabetes()
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    당뇨.data, 당뇨.target, test_size=0.25, random_state=42)

print("     " + "".join(f"{이름:>6}" for 이름 in 당뇨.feature_names) + "   시험 R²")
for 이름, 회귀 in [("선형", LinearRegression()), ("릿지", Ridge(alpha=10.0)),
                   ("라소", Lasso(alpha=1.0))]:
    모델 = make_pipeline(StandardScaler(), 회귀).fit(X_학습, y_학습)
    계수 = 모델[-1].coef_.round(1) + 0.0          # + 0.0은 -0.0을 0.0으로 정리
    print(f"{이름} " + "".join(f"{값:6.1f}" for 값 in 계수)
          + f"   {모델.score(X_시험, y_시험):.3f}")
