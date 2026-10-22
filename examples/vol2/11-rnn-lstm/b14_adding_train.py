# [2권 Chapter 11. RNN과 LSTM: 순서가 있는 데이터 · 11.7 긴 기억 시험: 멀리 떨어진 두 수 더하기 · manuscript-vol2/chapters/11-rnn-lstm.md:743]
import torch
from torch import nn


def 더하기_문제(개수: int, 길이: int, g: torch.Generator) -> tuple[torch.Tensor, torch.Tensor]:
    """앞 예제와 같은 문제: 표시된 두 숫자의 합 맞히기."""
    값 = torch.rand(개수, 길이, generator=g)
    표시 = torch.zeros(개수, 길이)
    표시[torch.arange(개수), torch.randint(0, 길이 // 2, (개수,), generator=g)] = 1.0
    표시[torch.arange(개수), torch.randint(길이 // 2, 길이, (개수,), generator=g)] = 1.0
    return torch.stack([값, 표시], dim=-1), (값 * 표시).sum(dim=1, keepdim=True)


class 더하기_모델(nn.Module):
    def __init__(self, 종류: type[nn.Module]) -> None:
        super().__init__()
        self.순환 = 종류(2, 32, batch_first=True)    # nn.RNN, nn.LSTM, nn.GRU 중 하나
        self.답 = nn.Linear(32, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        출력, _ = self.순환(x)                        # LSTM의 (h, c)도 _로 받아 넘긴다
        return self.답(출력[:, -1])                   # 마지막 시점의 메모로 답한다


def 실험(종류: type[nn.Module], 길이: int) -> tuple[float, float, list[float]]:
    torch.manual_seed(0)
    모델 = 더하기_모델(종류)
    옵티마이저 = torch.optim.Adam(모델.parameters(), lr=3e-3)
    g = torch.Generator().manual_seed(0)
    기록 = []
    for 단계 in range(1, 1501):                       # 매번 새 문제 64개로 1,500번
        x, y = 더하기_문제(64, 길이, g)
        손실 = nn.functional.mse_loss(모델(x), y)
        옵티마이저.zero_grad()
        손실.backward()
        nn.utils.clip_grad_norm_(모델.parameters(), max_norm=1.0)   # 8.9절의 안전벨트
        옵티마이저.step()
        if 단계 % 300 == 0:
            기록.append(round(손실.item(), 3))
    x, y = 더하기_문제(1000, 길이, torch.Generator().manual_seed(99))  # 시험 문제
    x.requires_grad_(True)
    예측 = 모델(x)
    기울기, = torch.autograd.grad(예측.sum(), x)        # 첫 시점까지 기울기가 닿는가
    return nn.functional.mse_loss(예측, y).item(), 기울기[:, 0].norm(dim=1).mean().item(), 기록


for 길이 in [10, 50]:
    for 종류 in [nn.RNN, nn.LSTM, nn.GRU]:
        mse, 첫_기울기, 기록 = 실험(종류, 길이)
        print(f"길이 {길이:2d}  {종류.__name__:4}  시험 MSE {mse:.4f}  첫 시점 기울기 {첫_기울기:.1e}")
        print(f"          300번마다 학습 손실 {기록}")
