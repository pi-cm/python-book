# [2권 Chapter 3. scikit-learn으로 보는 고전 머신러닝 · 3.3 로지스틱 회귀: 확률로 답하는 분류 · manuscript-vol2/chapters/03-classic-ml.md:234]
import numpy as np


def 시그모이드(z: np.ndarray) -> np.ndarray:
    """어떤 실수든 0과 1 사이 값으로 눌러 담는다."""
    return 1 / (1 + np.exp(-z))


점수 = np.array([-6.0, -2.0, -0.5, 0.0, 0.5, 2.0, 6.0])
for z, p in zip(점수, 시그모이드(점수)):
    print(f"점수 {z:+5.1f} → 확률 {p:.3f}")
