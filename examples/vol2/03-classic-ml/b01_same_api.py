# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 들어가며: 엑셀 표 같은 데이터에도 딥러닝이 필요할까요? · manuscript-vol2/chapters/03-classic-ml.md:20]
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42)

모델들 = {
    "최근접 이웃": make_pipeline(StandardScaler(), KNeighborsClassifier()),
    "로지스틱 회귀": make_pipeline(StandardScaler(), LogisticRegression()),
    "결정 트리": DecisionTreeClassifier(random_state=42),
}
for 이름, 모델 in 모델들.items():
    모델.fit(X_학습, y_학습)               # 배우기: 모델마다 똑같은 한 줄
    정확도 = 모델.score(X_시험, y_시험)     # 처음 보는 문제로 채점하기
    print(f"{이름}: 시험 정확도 {정확도:.3f}")
