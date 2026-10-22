# [2권 Chapter 5. 자동 미분과 경사하강법 · 5.12 torch.autograd.grad: 기울기를 직접 받기 · manuscript-vol2/chapters/05-autograd.md:1120]
import torch


def 모델(입력: torch.Tensor) -> torch.Tensor:
    """학습이 끝났다고 치는 모델: 기온과 습도로 판매량을 예측한다(예제용 식)."""
    기온, 습도 = 입력[0], 입력[1]
    return 2.5 * 기온 + 0.8 * 습도 + 0.05 * 기온 * 습도 - 15


오늘 = torch.tensor([30.0, 60.0], requires_grad=True)     # 기온 30°C, 습도 60%
예측 = 모델(오늘)
(민감도,) = torch.autograd.grad(예측, 오늘)               # 입력에 대한 기울기
print(f"예측 판매량: {예측.item():.1f}개")
print(f"기온 1°C당 {민감도[0]:.2f}개 (손으로: 2.5 + 0.05 × 60 = {2.5 + 0.05 * 60:.2f})")
print(f"습도 1%p당 {민감도[1]:.2f}개 (손으로: 0.8 + 0.05 × 30 = {0.8 + 0.05 * 30:.2f})")
