# [2권 Chapter 1. 머신러닝이란: 규칙을 짜지 않고 데이터로 배우기 · 1.3 머신러닝의 세 갈래 · manuscript-vol2/chapters/01-what-is-ml.md:272]
import random

당첨_확률 = [0.3, 0.5, 0.7]   # 기계마다 다른 당첨 확률 (에이전트는 모른다)
탐험_비율 = 0.1               # 열 번에 한 번은 아무 기계나 눌러 본다
rng = random.Random(0)

누른_횟수 = [0, 0, 0]
받은_보상 = [0, 0, 0]
for 회차 in range(1000):
    if rng.random() < 탐험_비율 or 0 in 누른_횟수:
        기계 = rng.randrange(3)                                  # 탐험
    else:
        기계 = max(range(3), key=lambda i: 받은_보상[i] / 누른_횟수[i])  # 활용
    보상 = 1 if rng.random() < 당첨_확률[기계] else 0
    누른_횟수[기계] += 1
    받은_보상[기계] += 보상

for i in range(3):
    추정 = 받은_보상[i] / 누른_횟수[i]
    print(f"기계 {i}: {누른_횟수[i]:4d}번 누름, 추정 당첨률 {추정:.2f} (실제 {당첨_확률[i]})")
print("1000번 중 당첨:", sum(받은_보상))
