# [2권 Chapter 6. nn.Module과 학습 루프: 모든 모델이 따르는 표준형 · 6.6 옵티마이저: 어떻게 고칠까 · manuscript-vol2/chapters/06-nn-module.md:653]
import torch


def 골짜기(점: torch.Tensor) -> torch.Tensor:
    """동서로 길고 남북으로 가파른 골짜기. 가장 낮은 곳은 (0, 0)."""
    return 점[0] ** 2 + 50 * 점[1] ** 2


def 내려가기(옵티마이저_만들기, 단계: int = 100) -> tuple[list[float], list[float]]:
    """(-4, 1)에서 출발해 골짜기 바닥으로 내려가며 높이를 기록한다."""
    점 = torch.tensor([-4.0, 1.0], requires_grad=True)
    옵티마이저 = 옵티마이저_만들기([점])
    기록 = []
    for _ in range(단계):
        옵티마이저.zero_grad()
        높이 = 골짜기(점)
        높이.backward()
        옵티마이저.step()
        기록.append(골짜기(점).item())
    return 기록, 점.detach().tolist()


후보 = {
    "SGD lr=0.01         ": lambda p: torch.optim.SGD(p, lr=0.01),
    "SGD lr=0.03         ": lambda p: torch.optim.SGD(p, lr=0.03),
    "SGD+momentum lr=0.01": lambda p: torch.optim.SGD(p, lr=0.01, momentum=0.9),
    "Adam lr=0.1         ": lambda p: torch.optim.Adam(p, lr=0.1),
}
print(" " * 21, "  10단계    30단계   100단계  마지막 위치")
for 이름, 만들기 in 후보.items():
    기록, 위치 = 내려가기(만들기)
    print(f"{이름} {기록[9]:9.4g} {기록[29]:9.4g} {기록[99]:9.4g}  ({위치[0]:.3f}, {위치[1]:.3g})")
