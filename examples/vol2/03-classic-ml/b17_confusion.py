# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.7 분류 모델 평가하기: 정확도만 보면 속는 이유 · manuscript-vol2/chapters/03-classic-ml.md:691]
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (confusion_matrix, f1_score, precision_score,
                             recall_score)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)
y = 1 - y                                # 1 = 악성 (찾고 싶은 쪽 = 양성 판정)
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42)
모델 = make_pipeline(StandardScaler(), LogisticRegression()).fit(X_학습, y_학습)
예측 = 모델.predict(X_시험)

표 = confusion_matrix(y_시험, 예측)
print(표)
tn, fp, fn, tp = 표.ravel()
print(f"TN={tn}, FP={fp}, FN={fn}, TP={tp}")

정밀도 = tp / (tp + fp)
재현율 = tp / (tp + fn)
f1 = 2 * 정밀도 * 재현율 / (정밀도 + 재현율)
print(f"직접 계산: 정밀도 {정밀도:.3f}, 재현율 {재현율:.3f}, F1 {f1:.3f}")
print(f"sklearn : 정밀도 {precision_score(y_시험, 예측):.3f}, "
      f"재현율 {recall_score(y_시험, 예측):.3f}, F1 {f1_score(y_시험, 예측):.3f}")
