# [2권 Chapter 5. 자동 미분과 경사하강법 · 5.11 미니배치 경사하강법 맛보기 · manuscript-vol2/chapters/05-autograd.md:1015]
import numpy as np
import torch

# 1,000일치 예제용 데이터(앞의 30일과 같은 규칙으로 만들었다)
rng = np.random.default_rng(1)
기온 = rng.uniform(18, 34, size=1000)
판매량 = 2.5 * 기온 - 15 + rng.normal(0, 4, size=1000)
x = torch.tensor((기온 - 기온.mean()) / 기온.std(), dtype=torch.float32)
y = torch.tensor(판매량, dtype=torch.float32)


def 학습(배치_크기: int, 에폭: int = 5, 학습률: float = 0.05) -> None:
    torch.manual_seed(0)
    w = torch.zeros((), requires_grad=True)
    b = torch.zeros((), requires_grad=True)
    고친_횟수 = 0
    기록 = []
    for _ in range(에폭):                         # 에폭: 데이터 전체를 한 바퀴 도는 것
        순서 = torch.randperm(len(x))              # 매 에폭 섞기
        for 시작 in range(0, len(x), 배치_크기):
            고를 = 순서[시작:시작 + 배치_크기]
            손실 = ((w * x[고를] + b - y[고를]) ** 2).mean()   # 일부만 보고 손실 계산
            손실.backward()
            with torch.no_grad():
                w -= 학습률 * w.grad
                b -= 학습률 * b.grad
                w.grad.zero_()
                b.grad.zero_()
            고친_횟수 += 1
        with torch.no_grad():
            기록.append(((w * x + b - y) ** 2).mean().item())  # 에폭 끝: 전체 데이터 손실
    print(f"배치 {배치_크기:4} | {고친_횟수:4}번 고침 |", " ".join(f"{v:7.2f}" for v in 기록))


print("                         에폭별 전체 손실: 1, 2, 3, 4, 5")
for 배치_크기 in [1000, 32, 1]:
    학습(배치_크기)

정답_w, 정답_b = np.polyfit(x.numpy(), y.numpy(), deg=1)
print(f"도달할 수 있는 가장 낮은 손실: {((정답_w * x + 정답_b - y) ** 2).mean().item():.2f}")
