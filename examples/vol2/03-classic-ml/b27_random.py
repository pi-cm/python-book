# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.10 하이퍼파라미터 탐색 · manuscript-vol2/chapters/03-classic-ml.md:1124]
from scipy.stats import loguniform, randint
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, train_test_split

X, y = load_breast_cancer(return_X_y=True)
y = 1 - y                                # 1 = 악성
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42)

분포 = {
    "learning_rate": loguniform(0.01, 0.3),   # 0.01~0.3을 자릿수 기준으로 고르게
    "max_leaf_nodes": randint(4, 32),         # 4 이상 32 미만 정수
    "min_samples_leaf": randint(5, 40),
}
탐색 = RandomizedSearchCV(HistGradientBoostingClassifier(random_state=0), 분포,
                          n_iter=15, scoring="roc_auc", random_state=0,
                          cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=0))
탐색.fit(X_학습, y_학습)                   # 15조합 × 5묶음 = 75번 학습

최고 = 탐색.best_params_
print(f"learning_rate={최고['learning_rate']:.4f}, max_leaf_nodes={최고['max_leaf_nodes']},"
      f" min_samples_leaf={최고['min_samples_leaf']}")
print(f"교차 검증 ROC-AUC: {탐색.best_score_:.4f}")
# best_estimator_는 최고 조합으로 학습 세트 전체를 다시 배운 모델
시험_점수 = roc_auc_score(y_시험, 탐색.predict_proba(X_시험)[:, 1])
print(f"시험 세트 ROC-AUC: {시험_점수:.4f}")
