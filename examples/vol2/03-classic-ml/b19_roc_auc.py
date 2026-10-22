# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.7 분류 모델 평가하기: 정확도만 보면 속는 이유 · manuscript-vol2/chapters/03-classic-ml.md:778]
from sklearn.datasets import load_breast_cancer
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)
y = 1 - y                                # 1 = 악성
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42)

모델들 = {
    "아무 정보 없이 찍기": DummyClassifier(strategy="prior"),
    "질문 두 번짜리 나무": DecisionTreeClassifier(max_depth=2, random_state=42),
    "로지스틱 회귀": make_pipeline(StandardScaler(), LogisticRegression()),
}
for 이름, 모델 in 모델들.items():
    점수 = 모델.fit(X_학습, y_학습).predict_proba(X_시험)[:, 1]
    print(f"{이름}: ROC-AUC {roc_auc_score(y_시험, 점수):.3f}")

# AUC의 뜻: 악성 한 명과 악성 아닌 한 명을 뽑았을 때 악성 쪽 점수가 더 높을 확률
악성, 정상 = 점수[y_시험 == 1], 점수[y_시험 == 0]
이김 = (악성[:, None] > 정상[None, :]).mean() + 0.5 * (악성[:, None] == 정상[None, :]).mean()
print(f"짝 {len(악성) * len(정상)}개를 직접 비교한 비율: {이김:.3f}")

fpr, tpr, 문턱들 = roc_curve(y_시험, 점수)
print("FPR(거짓 경보율):", fpr.round(3).tolist())
print("TPR(재현율):     ", tpr.round(3).tolist())
