# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.5 여럿이 함께: 랜덤 포레스트와 그래디언트 부스팅 · manuscript-vol2/chapters/03-classic-ml.md:425]
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

암 = load_breast_cancer()
X, y = 암.data, 1 - 암.target            # 1 = 악성
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42)

숲 = RandomForestClassifier(n_estimators=200, random_state=42).fit(X_학습, y_학습)
print(f"숲의 시험 정확도: {숲.score(X_시험, y_시험):.3f}")

# 확률이 가장 애매한 시험 환자 한 명에 대한 나무들의 투표
애매도 = abs(숲.predict_proba(X_시험)[:, 1] - 0.5)
환자 = X_시험[애매도.argmin()].reshape(1, -1)
표 = sum(int(그루.predict(환자)[0]) for 그루 in 숲.estimators_)
print(f"가장 애매한 환자: 악성 {표}표, 악성 아님 {200 - 표}표")

중요도 = 숲.feature_importances_
for i in 중요도.argsort()[::-1][:4]:
    print(f"{암.feature_names[i]:>20}: {중요도[i]:.3f}")
