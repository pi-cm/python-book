# [2권 Chapter 11. RNN과 LSTM: 순서가 있는 데이터 · 11.2 RNN 셀: 메모장을 고쳐 쓰며 읽기 · manuscript-vol2/chapters/11-rnn-lstm.md:179]
import torch
from torch import nn

torch.manual_seed(0)
rnn = nn.RNN(input_size=3, hidden_size=4, batch_first=True)
for 이름, p in rnn.named_parameters():
    print(f"{이름:14} {tuple(p.shape)}")

# 같은 가중치로 손으로 계산해 보기 (PyTorch는 x @ W.T 꼴로 가중치를 보관한다)
순서열 = torch.randn(2, 5, 3)
h = torch.zeros(2, 4)
for t in range(5):
    h = torch.tanh(순서열[:, t] @ rnn.weight_ih_l0.T + rnn.bias_ih_l0
                   + h @ rnn.weight_hh_l0.T + rnn.bias_hh_l0)

출력, h_n = rnn(순서열)
print("출력:", tuple(출력.shape), "h_n:", tuple(h_n.shape))
print("손 계산과 차이:", (h - h_n[0]).abs().max().item())
print("출력의 마지막 시점 == h_n?", torch.allclose(출력[:, -1], h_n[0]))
