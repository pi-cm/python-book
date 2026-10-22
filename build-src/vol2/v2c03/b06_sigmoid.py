import numpy as np


def 시그모이드(z: np.ndarray) -> np.ndarray:
    """어떤 실수든 0과 1 사이 값으로 눌러 담는다."""
    return 1 / (1 + np.exp(-z))


점수 = np.array([-6.0, -2.0, -0.5, 0.0, 0.5, 2.0, 6.0])
for z, p in zip(점수, 시그모이드(점수)):
    print(f"점수 {z:+5.1f} → 확률 {p:.3f}")
