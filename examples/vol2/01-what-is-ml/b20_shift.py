# [2권 Chapter 1. 머신러닝이란: 규칙을 짜지 않고 데이터로 배우기 · 1.11 딥러닝은 무엇이 다른가요? · manuscript-vol2/chapters/01-what-is-ml.md:1066]
import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

숫자 = load_digits()
X_학습, X_테스트, y_학습, y_테스트 = train_test_split(
    숫자.images, 숫자.target, test_size=0.3, random_state=0)

모델 = KNeighborsClassifier(n_neighbors=5).fit(X_학습.reshape(-1, 64), y_학습)


def 오른쪽으로_밀기(그림들: np.ndarray, 칸: int) -> np.ndarray:
    """그림 전체를 오른쪽으로 칸만큼 옮기고 빈자리는 0으로 채운다."""
    밀린 = np.zeros_like(그림들)
    밀린[:, :, 칸:] = 그림들[:, :, :8 - 칸]
    return 밀린


for 칸 in [0, 1, 2]:
    X_밀린 = 오른쪽으로_밀기(X_테스트, 칸) if 칸 else X_테스트
    print(f"오른쪽으로 {칸}칸 밀었을 때 정확도: {모델.score(X_밀린.reshape(-1, 64), y_테스트):.3f}")
