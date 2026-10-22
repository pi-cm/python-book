# [2권 Chapter 5. 자동 미분과 경사하강법 · 5.5 계산 그래프: PyTorch는 무엇을 기억하나 · manuscript-vol2/chapters/05-autograd.md:533]
import torch


def 요금(사용량: torch.Tensor) -> torch.Tensor:
    """100 넘게 쓰면 넘은 만큼은 단가가 두 배가 되는 누진 요금."""
    if 사용량 > 100:                          # 평범한 파이썬 if
        return 100 * 1.0 + (사용량 - 100) * 2.0
    return 사용량 * 1.0


for 값 in [80.0, 130.0]:
    u = torch.tensor(값, requires_grad=True)
    요금(u).backward()
    print(f"사용량 {값}: 요금 기울기 {u.grad.item()}")

u = torch.tensor(130.0, requires_grad=True)
결과 = 요금(u)
결과.backward()
try:
    결과.backward()                          # 같은 그래프로 한 번 더?
except RuntimeError as e:
    print("오류:", str(e).split(".")[0])
