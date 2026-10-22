# [2권 Chapter 5. 자동 미분과 경사하강법 · 5.3 선형 회귀를 손으로 학습하기 · manuscript-vol2/chapters/05-autograd.md:274]
import numpy as np

rng = np.random.default_rng(0)
기온 = rng.uniform(18, 34, size=30).round(1)
판매량 = (2.5 * 기온 - 15 + rng.normal(0, 4, size=30)).round()
x = (기온 - 기온.mean()) / 기온.std()          # 표준화: 평균 0, 표준편차 1
y = 판매량


def 손실(w: float, b: float) -> float:
    return float(((w * x + b - y) ** 2).mean())


def 손_기울기(w: float, b: float) -> tuple[float, float]:
    """손으로 미분한 공식: 오차 = 예측 - 정답."""
    오차 = w * x + b - y
    return float((2 * 오차 * x).mean()), float((2 * 오차).mean())


w, b = 0.0, 0.0
h = 1e-5
잰_w = (손실(w + h, b) - 손실(w - h, b)) / (2 * h)
잰_b = (손실(w, b + h) - 손실(w, b - h)) / (2 * h)
공식_w, 공식_b = 손_기울기(w, b)
print(f"w 방향: 수치 미분 {잰_w:.4f}, 공식 {공식_w:.4f}")
print(f"b 방향: 수치 미분 {잰_b:.4f}, 공식 {공식_b:.4f}")
