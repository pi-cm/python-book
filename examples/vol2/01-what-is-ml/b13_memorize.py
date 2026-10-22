# [2권 Chapter 1. 머신러닝이란: 규칙을 짜지 않고 데이터로 배우기 · 1.7 일반화와 과적합: 외우기와 이해하기 · manuscript-vol2/chapters/01-what-is-ml.md:659]
import numpy as np
from sklearn.datasets import load_iris

X, y = load_iris(return_X_y=True)
섞은_번호 = np.random.default_rng(42).permutation(len(X))
X_학습, y_학습 = X[섞은_번호[30:]], y[섞은_번호[30:]]
X_테스트, y_테스트 = X[섞은_번호[:30]], y[섞은_번호[:30]]

# 외우기 모델: 특성 네 개를 통째로 열쇠로 삼아 정답을 적어 둔다
암기장 = {tuple(특성): 정답 for 특성, 정답 in zip(X_학습, y_학습)}


def 외워서_답하기(특성: np.ndarray) -> int | None:
    return 암기장.get(tuple(특성))      # 처음 보는 꽃이면 None


학습_맞음 = sum(외워서_답하기(x) == t for x, t in zip(X_학습, y_학습))
테스트_답 = [외워서_답하기(x) for x in X_테스트]
테스트_맞음 = sum(답 == t for 답, t in zip(테스트_답, y_테스트))
print(f"학습 데이터: {학습_맞음}/{len(y_학습)} 맞힘")
print(f"테스트 데이터: {테스트_맞음}/{len(y_테스트)} 맞힘, "
      f"모른다(None): {테스트_답.count(None)}송이")
