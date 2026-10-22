# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.9 교차 검증: 모의고사는 한 번보다 다섯 번 · manuscript-vol2/chapters/03-classic-ml.md:991]
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score, cross_validate
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)
y = 1 - y                                # 1 = 악성
모델 = make_pipeline(StandardScaler(), LogisticRegression())
접기 = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)

점수 = cross_val_score(모델, X, y, cv=접기)               # 기본 채점: 정확도
print("정확도 5개:", 점수.round(3), f"→ 평균 {점수.mean():.3f}")

결과 = cross_validate(모델, X, y, cv=접기, return_train_score=True,
                      scoring=["accuracy", "recall", "roc_auc"])
for 지표 in ["accuracy", "recall", "roc_auc"]:
    print(f"{지표:>8}: 학습 {결과['train_' + 지표].mean():.3f}, "
          f"검증 {결과['test_' + 지표].mean():.3f} ± {결과['test_' + 지표].std():.3f}")
