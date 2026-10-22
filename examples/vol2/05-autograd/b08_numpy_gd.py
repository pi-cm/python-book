# [2권 Chapter 5. 자동 미분과 경사하강법 · 5.3 선형 회귀를 손으로 학습하기 · manuscript-vol2/chapters/05-autograd.md:316]
import numpy as np

rng = np.random.default_rng(0)
기온 = rng.uniform(18, 34, size=30).round(1)
판매량 = (2.5 * 기온 - 15 + rng.normal(0, 4, size=30)).round()
x = (기온 - 기온.mean()) / 기온.std()
y = 판매량

w, b = 0.0, 0.0
학습률 = 0.1
for 반복 in range(1, 101):
    오차 = w * x + b - y
    손실 = (오차 ** 2).mean()
    기울기_w = (2 * 오차 * x).mean()
    기울기_b = (2 * 오차).mean()
    w -= 학습률 * 기울기_w
    b -= 학습률 * 기울기_b
    if 반복 in (1, 5, 10, 20, 50, 100):
        print(f"{반복:3}번째: 손실 {손실:8.3f}, w = {w:.4f}, b = {b:.4f}")

정답_w, 정답_b = np.polyfit(x, y, deg=1)      # 한 번에 푸는 공식(최소제곱법)
print(f"polyfit 정답: w = {정답_w:.4f}, b = {정답_b:.4f}")
print(f"기온 1°C당 판매량 변화: {w / 기온.std():.3f}개")
