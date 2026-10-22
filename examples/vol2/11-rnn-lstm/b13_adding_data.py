# [2권 Chapter 11. RNN과 LSTM: 순서가 있는 데이터 · 11.7 긴 기억 시험: 멀리 떨어진 두 수 더하기 · manuscript-vol2/chapters/11-rnn-lstm.md:700]
import torch


def 더하기_문제(개수: int, 길이: int, g: torch.Generator) -> tuple[torch.Tensor, torch.Tensor]:
    """0~1 사이 숫자 줄에서 표시된 두 칸(앞 절반에 하나, 뒤 절반에 하나)의 합을 맞히는 문제."""
    값 = torch.rand(개수, 길이, generator=g)
    표시 = torch.zeros(개수, 길이)
    앞 = torch.randint(0, 길이 // 2, (개수,), generator=g)
    뒤 = torch.randint(길이 // 2, 길이, (개수,), generator=g)
    표시[torch.arange(개수), 앞] = 1.0
    표시[torch.arange(개수), 뒤] = 1.0
    x = torch.stack([값, 표시], dim=-1)          # (개수, 길이, 특성 2): 숫자와 표시
    y = (값 * 표시).sum(dim=1, keepdim=True)      # 표시된 두 숫자의 합
    return x, y


g = torch.Generator().manual_seed(0)
x, y = 더하기_문제(1, 10, g)
print("숫자:", [round(v, 2) for v in x[0, :, 0].tolist()])
print("표시:", x[0, :, 1].int().tolist())
print("정답:", round(y.item(), 4))

# 아무것도 못 배운 모델은 늘 평균(1.0)을 말한다. 그때의 MSE는?
_, y = 더하기_문제(100_000, 50, g)
print(f"늘 1.0이라고 답할 때 MSE: {((y - 1.0) ** 2).mean().item():.4f}")
