# [2권 Chapter 1. 머신러닝이란: 규칙을 짜지 않고 데이터로 배우기 · 1.11 딥러닝은 무엇이 다른가요? · manuscript-vol2/chapters/01-what-is-ml.md:1027]
import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

숫자 = load_digits()
그림들 = 숫자.images                     # (1797, 8, 8)


def 손으로_만든_특성(그림들: np.ndarray) -> np.ndarray:
    """사람이 '숫자를 구별하는 데 쓸 만하다'고 생각한 특성 네 개."""
    전체_잉크 = 그림들.sum(axis=(1, 2))
    위_비율 = 그림들[:, :4, :].sum(axis=(1, 2)) / 전체_잉크
    왼쪽_비율 = 그림들[:, :, :4].sum(axis=(1, 2)) / 전체_잉크
    가운데_잉크 = 그림들[:, 2:6, 2:6].sum(axis=(1, 2)) / 전체_잉크
    return np.column_stack([전체_잉크, 위_비율, 왼쪽_비율, 가운데_잉크])


for 이름, X in [("손으로 만든 특성 4개", 손으로_만든_특성(그림들)),
                ("픽셀 64개 그대로", 숫자.data)]:
    X_학습, X_테스트, y_학습, y_테스트 = train_test_split(
        X, 숫자.target, test_size=0.3, random_state=0)
    평균, 표준편차 = X_학습.mean(axis=0), X_학습.std(axis=0) + 1e-9
    모델 = KNeighborsClassifier(n_neighbors=5).fit((X_학습 - 평균) / 표준편차, y_학습)
    print(f"{이름}: 정확도 {모델.score((X_테스트 - 평균) / 표준편차, y_테스트):.3f}")
