# [2권 Chapter 11. RNN과 LSTM: 순서가 있는 데이터 · 11.4 기울기 소실과 폭주 · manuscript-vol2/chapters/11-rnn-lstm.md:523]
import torch
from torch import nn

torch.manual_seed(0)
길이 = 100
x = torch.randn(1, 길이, 8, requires_grad=True)    # 길이 100짜리 순서열 하나


def 시점별_기울기(rnn: nn.RNN) -> torch.Tensor:
    """마지막 출력이 각 시점의 입력에 얼마나 민감한지(기울기의 크기)를 잰다."""
    출력, _ = rnn(x)
    기울기, = torch.autograd.grad(출력[0, -1].sum(), x)
    return 기울기[0].norm(dim=1)                    # 시점마다 하나의 크기


torch.manual_seed(0)
기본 = nn.RNN(8, 32, batch_first=True)
torch.manual_seed(0)
큰_가중치 = nn.RNN(8, 32, batch_first=True)
with torch.no_grad():
    큰_가중치.weight_hh_l0.mul_(4)                 # 메모 → 메모 가중치만 4배로

시점들 = [99, 95, 90, 80, 50, 0]
print("시점      " + "".join(f"{t:>10}" for t in 시점들))
for 이름, rnn in [("기본 RNN", 기본), ("W_h 4배", 큰_가중치)]:
    크기 = 시점별_기울기(rnn)
    print(f"{이름:8}" + "".join(f"{크기[t].item():10.2e}" for t in 시점들))
