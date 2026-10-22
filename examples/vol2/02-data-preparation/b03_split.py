# [2권 Chapter 2. 데이터 준비: 모델에 넣기 전에 할 일 · 2.2 학습·검증·테스트로 나누기 · manuscript-vol2/chapters/02-data-preparation.md:150]
import numpy as np
from sklearn.model_selection import train_test_split

# 손님 500명 × 특성 2개 (예제용). 0열에 손님 번호를 넣어 두면 누가 어디로 갔는지 보인다
X = np.column_stack([np.arange(500), np.random.default_rng(0).normal(size=500)])
y = np.arange(500) % 2

# 1단계: 테스트용 20%를 먼저 떼어 금고에 넣는다
X_나머지, X_테스트, y_나머지, y_테스트 = train_test_split(
    X, y, test_size=0.2, random_state=42)
# 2단계: 남은 80% 가운데 25%(전체의 20%)를 검증용으로
X_학습, X_검증, y_학습, y_검증 = train_test_split(
    X_나머지, y_나머지, test_size=0.25, random_state=42)

print("학습/검증/테스트:", len(X_학습), len(X_검증), len(X_테스트))
print("테스트에 들어간 손님 번호:", X_테스트[:6, 0].astype(int))

_, X_다시, _, _ = train_test_split(X, y, test_size=0.2, random_state=42)
print("같은 씨앗으로 다시:", X_다시[:6, 0].astype(int))
_, X_다른, _, _ = train_test_split(X, y, test_size=0.2, random_state=7)
print("씨앗을 바꾸면:    ", X_다른[:6, 0].astype(int))
