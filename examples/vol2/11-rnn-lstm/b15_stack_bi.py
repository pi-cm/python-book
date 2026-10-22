# [2권 Chapter 11. RNN과 LSTM: 순서가 있는 데이터 · 11.8 층 쌓기와 양방향 · manuscript-vol2/chapters/11-rnn-lstm.md:826]
import torch
from torch import nn

torch.manual_seed(0)
x = torch.randn(2, 7, 8)                          # (배치 2, 길이 7, 특성 8)

설정들 = {"한 층": {}, "두 층": dict(num_layers=2, dropout=0.2),
          "양방향": dict(bidirectional=True), "두 층 양방향": dict(num_layers=2, bidirectional=True)}
for 이름, 설정 in 설정들.items():
    lstm = nn.LSTM(8, 16, batch_first=True, **설정)
    출력, (h_n, c_n) = lstm(x)
    개수 = sum(p.numel() for p in lstm.parameters())
    print(f"{이름}: 출력 {tuple(출력.shape)}, h_n {tuple(h_n.shape)}, 파라미터 {개수:,}개")

# 양방향 출력의 앞 16칸은 정방향, 뒤 16칸은 역방향
양방향 = nn.LSTM(8, 16, batch_first=True, bidirectional=True)
출력, (h_n, _) = 양방향(x)
print("정방향 마지막 = 출력[:, -1, :16]?", torch.allclose(h_n[0], 출력[:, -1, :16]))
print("역방향 마지막 = 출력[:, 0, 16:]?", torch.allclose(h_n[1], 출력[:, 0, 16:]))
양쪽_요약 = torch.cat([h_n[-2], h_n[-1]], dim=1)   # 분류에 쓸 때는 둘을 이어 붙인다
print("양쪽 요약:", tuple(양쪽_요약.shape))
