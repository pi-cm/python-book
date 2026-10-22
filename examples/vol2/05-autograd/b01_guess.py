# [2권 Chapter 5. 자동 미분과 경사하강법 · 들어가며: 안개 낀 산에서 내려오려면? · manuscript-vol2/chapters/05-autograd.md:21]
import numpy as np

# 30일 동안의 기온(°C)과 아이스크림 판매량(개). 예제용으로 만든 데이터입니다.
rng = np.random.default_rng(0)
기온 = rng.uniform(18, 34, size=30).round(1)
판매량 = (2.5 * 기온 - 15 + rng.normal(0, 4, size=30)).round()
print("기온  :", 기온[:5])
print("판매량:", 판매량[:5])


def 평균제곱오차(w: float, b: float) -> float:
    """직선 '판매량 = w × 기온 + b'가 실제 판매량에서 평균적으로 얼마나 벗어나는지."""
    예측 = w * 기온 + b
    return float(((예측 - 판매량) ** 2).mean())


for w, b in [(2.0, 0.0), (2.0, -5.0), (2.5, -10.0), (3.0, -20.0)]:
    print(f"w={w}, b={b:6.1f} → 오차 {평균제곱오차(w, b):7.2f}")
