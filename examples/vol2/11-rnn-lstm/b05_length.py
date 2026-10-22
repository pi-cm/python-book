# [2권 Chapter 11. RNN과 LSTM: 순서가 있는 데이터 · 11.2 RNN 셀: 메모장을 고쳐 쓰며 읽기 · manuscript-vol2/chapters/11-rnn-lstm.md:224]
import torch
from torch import nn

torch.manual_seed(0)
rnn = nn.RNN(input_size=3, hidden_size=4, batch_first=True)
print("파라미터 수:", sum(p.numel() for p in rnn.parameters()))

for 길이 in [1, 5, 500]:                   # 같은 모델에 길이가 다른 입력
    출력, h_n = rnn(torch.randn(2, 길이, 3))
    print(f"길이 {길이:3d}: 출력 {tuple(출력.shape)}, h_n {tuple(h_n.shape)}")

# 처음 메모장을 직접 넘길 수도 있다: (층 수, 배치, 메모 크기)
h0 = torch.zeros(1, 2, 4)
앞부분, h_중간 = rnn(torch.randn(2, 3, 3), h0)
뒷부분, h_끝 = rnn(torch.randn(2, 2, 3), h_중간)   # 이어서 읽기
print("이어 읽은 출력:", tuple(앞부분.shape), tuple(뒷부분.shape))

# batch_first를 빼면 (길이, 배치, 특성) 순서를 기대한다
rnn_기본 = nn.RNN(input_size=3, hidden_size=4)
출력, _ = rnn_기본(torch.randn(5, 2, 3))
print("batch_first=False 출력:", tuple(출력.shape))
