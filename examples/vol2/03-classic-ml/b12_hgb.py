# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.5 여럿이 함께: 랜덤 포레스트와 그래디언트 부스팅 · manuscript-vol2/chapters/03-classic-ml.md:501]
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split

X, y = load_breast_cancer(return_X_y=True)
y = 1 - y                                # 1 = 악성
X_학습, X_시험, y_학습, y_시험 = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42)

부스팅 = HistGradientBoostingClassifier(random_state=42).fit(X_학습, y_학습)
print(f"그래디언트 부스팅 시험 정확도: {부스팅.score(X_시험, y_시험):.3f}")
print("실제로 만든 나무 수:", 부스팅.n_iter_)

# 값의 10%를 일부러 지워도(결측치) 그대로 학습한다
rng = np.random.default_rng(0)
X_구멍 = X_학습.copy()
X_구멍[rng.random(X_구멍.shape) < 0.1] = np.nan
print("빈칸 개수:", np.isnan(X_구멍).sum())
부스팅.fit(X_구멍, y_학습)
print(f"빈칸 있는 데이터로 배운 뒤 시험 정확도: {부스팅.score(X_시험, y_시험):.3f}")
