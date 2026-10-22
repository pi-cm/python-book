# [2권 Chapter 17. 분산·대규모 학습: 메모리를 아끼고 GPU를 늘리기 · 17.2 그래디언트 누적: 큰 배치를 나눠 담기 · manuscript-vol2/chapters/17-distributed-training.md:145]
import torch
from torch import nn

torch.manual_seed(0)
X = torch.randn(64, 10)                 # 예제용으로 만든 데이터 64개
y = torch.randn(64, 1)
손실함수 = nn.MSELoss()


def 새_모델() -> nn.Module:
    """매번 똑같은 초깃값으로 시작하는 작은 모델."""
    torch.manual_seed(1)
    return nn.Sequential(nn.Linear(10, 32), nn.ReLU(), nn.Linear(32, 1))


def 기울기_모으기(모델: nn.Module, 단계: int, 나누기: bool = True) -> None:
    """64개를 단계 수만큼 나눠 forward/backward하고 기울기를 .grad에 쌓는다."""
    for xb, yb in zip(X.chunk(단계), y.chunk(단계)):
        손실 = 손실함수(모델(xb), yb)
        (손실 / 단계 if 나누기 else 손실).backward()


큰배치 = 새_모델()
기울기_모으기(큰배치, 단계=1)            # 64개를 한 번에
누적 = 새_모델()
기울기_모으기(누적, 단계=4)              # 16개씩 네 번
잊음 = 새_모델()
기울기_모으기(잊음, 단계=4, 나누기=False)  # 손실을 4로 나누는 것을 잊으면

차이 = max((a.grad - b.grad).abs().max().item()
         for a, b in zip(큰배치.parameters(), 누적.parameters()))
print(f"64개 한 번 vs 16개×4번 누적: 기울기 최대 차이 {차이:.1e}")
print(f"나누기를 잊으면 기울기가 {(잊음[0].weight.grad / 큰배치[0].weight.grad).mean():.2f}배")


def 학습(단계: int) -> list[float]:
    """같은 64개로 다섯 걸음 학습하고, 걸음마다 전체 손실을 기록한다."""
    모델 = 새_모델()
    옵티마이저 = torch.optim.SGD(모델.parameters(), lr=0.1)
    기록 = []
    for _ in range(5):
        옵티마이저.zero_grad()
        기울기_모으기(모델, 단계)
        옵티마이저.step()                   # 누적이 끝난 뒤에 한 번만 고친다
        with torch.no_grad():
            기록.append(round(손실함수(모델(X), y).item(), 6))
    return 기록


for 단계 in (1, 4, 8):
    print(f"{64 // 단계:2}개씩 {단계}번 누적:", 학습(단계))
