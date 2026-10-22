# [2권 Chapter 11. RNN과 LSTM: 순서가 있는 데이터 · 11.9 길이가 다른 순서열: pack_padded_sequence · manuscript-vol2/chapters/11-rnn-lstm.md:876]
import torch
from torch import nn
from torch.nn.utils.rnn import pad_sequence

torch.manual_seed(0)
rnn = nn.RNN(2, 4, batch_first=True)
짧은 = torch.randn(3, 2)                          # 길이 3
긴 = torch.randn(6, 2)                            # 길이 6
배치 = pad_sequence([짧은, 긴], batch_first=True)  # 짧은 쪽 뒤를 0으로 채워 (2, 6, 2)
print("패딩한 배치:", tuple(배치.shape))

출력, h_n = rnn(배치)
_, h_혼자 = rnn(짧은.unsqueeze(0))                 # 짧은 문장만 따로 읽었을 때
print("혼자 읽은 마지막 메모:", [round(v, 3) for v in h_혼자[0, 0].tolist()])
print("배치의 h_n           :", [round(v, 3) for v in h_n[0, 0].tolist()])
print("배치의 3번째 시점    :", [round(v, 3) for v in 출력[0, 2].tolist()])
