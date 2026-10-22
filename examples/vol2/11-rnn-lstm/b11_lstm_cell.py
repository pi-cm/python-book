# [2권 Chapter 11. RNN과 LSTM: 순서가 있는 데이터 · 11.5 LSTM: 기억을 따로 나르는 벨트 · manuscript-vol2/chapters/11-rnn-lstm.md:599]
import torch
from torch import nn

torch.manual_seed(0)
lstm = nn.LSTM(input_size=3, hidden_size=4, batch_first=True)
print("weight_ih_l0:", tuple(lstm.weight_ih_l0.shape), "weight_hh_l0:", tuple(lstm.weight_hh_l0.shape))


def lstm_셀(x: torch.Tensor, h: torch.Tensor, c: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """문 세 개와 새 내용 후보로 기억 c와 메모 h를 고쳐 쓴다."""
    점수 = (x @ lstm.weight_ih_l0.T + lstm.bias_ih_l0
            + h @ lstm.weight_hh_l0.T + lstm.bias_hh_l0)      # (배치, 4 × 4)
    i, f, g, o = 점수.chunk(4, dim=1)          # PyTorch의 순서: 입력·망각·후보·출력
    입력문, 망각문, 출력문 = torch.sigmoid(i), torch.sigmoid(f), torch.sigmoid(o)
    후보 = torch.tanh(g)
    c = 망각문 * c + 입력문 * 후보            # 지울 만큼 지우고, 적을 만큼 더한다
    h = 출력문 * torch.tanh(c)                # 기억 중 지금 꺼내 보일 만큼만
    return h, c


순서열 = torch.randn(2, 5, 3)
h, c = torch.zeros(2, 4), torch.zeros(2, 4)
for t in range(5):
    h, c = lstm_셀(순서열[:, t], h, c)

출력, (h_n, c_n) = lstm(순서열)             # LSTM은 (h_n, c_n) 두 개를 돌려준다
print("출력:", tuple(출력.shape), "h_n:", tuple(h_n.shape), "c_n:", tuple(c_n.shape))
print("h 차이:", (h - h_n[0]).abs().max().item(), " c 차이:", (c - c_n[0]).abs().max().item())
print("기억 c :", [round(v, 3) for v in c[0].tolist()])
print("메모 h :", [round(v, 3) for v in h[0].tolist()])
