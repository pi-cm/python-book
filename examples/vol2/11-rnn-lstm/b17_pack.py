# [2권 Chapter 11. RNN과 LSTM: 순서가 있는 데이터 · 11.9 길이가 다른 순서열: pack_padded_sequence · manuscript-vol2/chapters/11-rnn-lstm.md:908]
import torch
from torch import nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence, pad_sequence

torch.manual_seed(0)
rnn = nn.RNN(2, 4, batch_first=True)
문장들 = [torch.randn(3, 2), torch.randn(6, 2), torch.randn(4, 2)]
길이 = torch.tensor([len(s) for s in 문장들])
배치 = pad_sequence(문장들, batch_first=True)

# 길이를 알려 주고 '꾸러미'로 싸면, 채운 칸은 아예 계산하지 않는다
꾸러미 = pack_padded_sequence(배치, 길이, batch_first=True, enforce_sorted=False)
print("실제 계산할 칸:", tuple(꾸러미.data.shape), "시점별 문장 수:", 꾸러미.batch_sizes.tolist())

출력_꾸러미, h_n = rnn(꾸러미)
for i, 문장 in enumerate(문장들):
    _, h_혼자 = rnn(문장.unsqueeze(0))
    print(f"문장 {i} (길이 {len(문장)}): 혼자 읽은 것과 같은가?", torch.allclose(h_n[0, i], h_혼자[0, 0], atol=1e-6))

출력, 출력_길이 = pad_packed_sequence(출력_꾸러미, batch_first=True)   # 다시 (배치, 길이, 특성)으로
print("되돌린 출력:", tuple(출력.shape), 출력_길이.tolist())
print("채운 칸의 출력은 0:", 출력[0, 3:].abs().sum().item())
