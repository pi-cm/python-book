# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.10 하이퍼파라미터 탐색 · manuscript-vol2/chapters/03-classic-ml.md:1072]
import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)
y = 1 - y                                # 1 = 악성
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42)

파이프 = make_pipeline(StandardScaler(), KNeighborsClassifier())
후보 = {
    "kneighborsclassifier__n_neighbors": [1, 3, 5, 9, 15, 25],   # 단계이름__설정이름
    "kneighborsclassifier__weights": ["uniform", "distance"],
}
탐색 = GridSearchCV(파이프, 후보, scoring="f1",
                    cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=0))
탐색.fit(X_학습, y_학습)                   # 6 × 2 = 12조합 × 5묶음 = 60번 학습

print("가장 좋은 조합:", 탐색.best_params_)
print(f"그 조합의 교차 검증 F1: {탐색.best_score_:.3f}")
표 = pd.DataFrame(탐색.cv_results_)[["param_kneighborsclassifier__n_neighbors",
                                     "param_kneighborsclassifier__weights",
                                     "mean_test_score", "rank_test_score"]]
표.columns = ["n_neighbors", "weights", "mean_f1", "rank"]
표 = 표.round(3)
print(표.sort_values("rank").head(4).to_string(index=False))
