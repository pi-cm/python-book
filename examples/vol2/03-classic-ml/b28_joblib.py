# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.11 모델 저장하고 불러오기 · manuscript-vol2/chapters/03-classic-ml.md:1172]
from pathlib import Path

import joblib
import sklearn
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)
y = 1 - y                                # 1 = 악성
모델 = make_pipeline(StandardScaler(), LogisticRegression()).fit(X, y)

폴더 = Path("models")
폴더.mkdir(exist_ok=True)
경로 = 폴더 / "cancer_lr.joblib"
joblib.dump({"model": 모델, "sklearn_version": sklearn.__version__}, 경로)
print(f"저장: {경로} ({경로.stat().st_size:,}바이트)")

꾸러미 = joblib.load(경로)                # 다른 프로그램에서 불러온다고 생각하자
불러온_모델 = 꾸러미["model"]
print("저장할 때 버전:", 꾸러미["sklearn_version"], "/ 지금 버전:", sklearn.__version__)
print("예측 비교(10명):", 모델.predict(X[::57]), 불러온_모델.predict(X[::57]))
print("확률까지 모두 같은가:", (모델.predict_proba(X) == 불러온_모델.predict_proba(X)).all())
print("단계 이름:", list(불러온_모델.named_steps))
