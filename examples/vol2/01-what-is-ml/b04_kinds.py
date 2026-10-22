# [2권 Chapter 1. 머신러닝이란: 규칙을 짜지 않고 데이터로 배우기 · 1.3 머신러닝의 세 갈래 · manuscript-vol2/chapters/01-what-is-ml.md:210]
import numpy as np
from sklearn.datasets import load_diabetes, load_iris

분류용 = load_iris()      # 꽃의 품종 맞히기
회귀용 = load_diabetes()  # 1년 뒤 당뇨 진행 정도(숫자) 맞히기

print("분류 레이블 예:", 분류용.target[[0, 1, 50, 51, 100]])
print("분류 레이블 종류:", np.unique(분류용.target))
print("회귀 레이블 예:", 회귀용.target[:5])
print(f"회귀 레이블은 {len(np.unique(회귀용.target))}가지 값, "
      f"범위 {회귀용.target.min():.0f}~{회귀용.target.max():.0f}")
