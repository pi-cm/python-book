# [2권 Chapter 2. 데이터 준비: 모델에 넣기 전에 할 일 · 2.6 스케일링: 단위 맞추기 · manuscript-vol2/chapters/02-data-preparation.md:642]
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# 유방 종양 569건의 측정값 30가지, 양성/악성 (scikit-learn 내장 데이터)
X, y = load_breast_cancer(return_X_y=True, as_frame=True)
print(X[["mean area", "mean smoothness"]].describe().loc[["min", "max"]])
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    X, y, test_size=0.25, random_state=0, stratify=y)

스케일러 = StandardScaler().fit(X_학습)      # 학습 데이터로만 평균·표준편차를 배운다
for 이름, 학습, 시험 in [("그대로", X_학습, X_시험),
                         ("표준화", 스케일러.transform(X_학습), 스케일러.transform(X_시험))]:
    모델 = LogisticRegression(max_iter=1000).fit(학습, y_학습)   # 최대 1000번까지 고쳐 본다
    print(f"{이름}: 고친 횟수 {모델.n_iter_[0]:4d}번, 시험 정확도 {모델.score(시험, y_시험):.1%}")
