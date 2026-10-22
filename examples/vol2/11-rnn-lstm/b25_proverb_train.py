# [2권 Chapter 11. RNN과 LSTM: 순서가 있는 데이터 · 11.11 실습: 속담 짓는 글자 단위 LSTM · manuscript-vol2/chapters/11-rnn-lstm.md:1406]
from pathlib import Path

import torch
from torch import nn

글 = Path("data/속담.txt").read_text(encoding="utf-8")
글자들 = sorted(set(글))
번호 = {글자: i for i, 글자 in enumerate(글자들)}
전체 = torch.tensor([번호[글자] for 글자 in 글])


class 속담_LSTM(nn.Module):
    def __init__(self, 글자_수: int, 임베딩_크기: int = 32, 메모_크기: int = 128) -> None:
        super().__init__()
        self.임베딩 = nn.Embedding(글자_수, 임베딩_크기)
        self.lstm = nn.LSTM(임베딩_크기, 메모_크기, batch_first=True)
        self.다음_글자 = nn.Linear(메모_크기, 글자_수)

    def forward(self, x: torch.Tensor, 상태: tuple | None = None) -> tuple[torch.Tensor, tuple]:
        출력, 상태 = self.lstm(self.임베딩(x), 상태)
        return self.다음_글자(출력), 상태          # 모든 시점에서 다음 글자 점수를 낸다


def 짓기(모델: nn.Module, 시작: str, g: torch.Generator, 최대: int = 40) -> str:
    """시작 글자들을 읽힌 뒤, 줄바꿈이 나올 때까지 한 글자씩 뽑아 잇는다."""
    모델.eval()
    x, 상태, 결과 = torch.tensor([[번호[c] for c in 시작]]), None, 시작
    with torch.no_grad():
        for _ in range(최대):
            점수, 상태 = 모델(x, 상태)               # 상태를 넘겨 이어서 읽는다
            확률 = 점수[0, -1].softmax(dim=0)
            다음 = torch.multinomial(확률, 1, generator=g).item()   # 확률대로 하나 뽑기
            if 글자들[다음] == "\n":
                break
            결과 += 글자들[다음]
            x = torch.tensor([[다음]])
    모델.train()
    return 결과.strip()


torch.manual_seed(0)
모델 = 속담_LSTM(len(글자들))
옵티마이저 = torch.optim.Adam(모델.parameters(), lr=3e-3)
길이 = 40
시작점들 = torch.arange(len(전체) - 길이)           # 40글자 조각을 어디서든 잘라 쓴다
print("파라미터:", f"{sum(p.numel() for p in 모델.parameters()):,}개")
for 에폭 in range(1, 61):
    합, 횟수 = 0.0, 0
    for 묶음 in 시작점들[torch.randperm(len(시작점들))].split(64):
        조각 = 전체[묶음.unsqueeze(1) + torch.arange(길이 + 1)]   # (64, 41)
        점수, _ = 모델(조각[:, :-1])
        손실 = nn.functional.cross_entropy(점수.reshape(-1, len(글자들)), 조각[:, 1:].reshape(-1))
        옵티마이저.zero_grad()
        손실.backward()
        nn.utils.clip_grad_norm_(모델.parameters(), max_norm=1.0)
        옵티마이저.step()
        합, 횟수 = 합 + 손실.item(), 횟수 + 1
    if 에폭 in (1, 5, 10, 20, 40, 60):
        g = torch.Generator().manual_seed(0)
        print(f"{에폭:2d}에폭 손실 {합 / 횟수:.3f} | {짓기(모델, '가', g)} | {짓기(모델, '호랑이', g)}")

torch.save({"가중치": 모델.state_dict(), "글자들": 글자들}, "속담_lstm.pt")
