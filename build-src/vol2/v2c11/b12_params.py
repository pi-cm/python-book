import torch
from torch import nn

입력_크기, 메모_크기 = 8, 32
for 종류 in [nn.RNN, nn.GRU, nn.LSTM]:
    torch.manual_seed(0)
    층 = 종류(입력_크기, 메모_크기, batch_first=True)
    개수 = sum(p.numel() for p in 층.parameters())
    출력, 상태 = 층(torch.randn(2, 10, 입력_크기))
    상태_모양 = [tuple(s.shape) for s in 상태] if isinstance(상태, tuple) else tuple(상태.shape)
    print(f"{종류.__name__:4} 파라미터 {개수:5,}개  가중치 줄 수 {층.weight_ih_l0.shape[0]:3}  상태 {상태_모양}")

기본 = 메모_크기 * 입력_크기 + 메모_크기 * 메모_크기 + 2 * 메모_크기
print(f"RNN 한 벌: {기본:,}개 → GRU는 3벌 {3 * 기본:,}개, LSTM은 4벌 {4 * 기본:,}개")
