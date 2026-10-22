# [2권 Chapter 11. RNN과 LSTM: 순서가 있는 데이터 · 11.11 실습: 속담 짓는 글자 단위 LSTM · manuscript-vol2/chapters/11-rnn-lstm.md:1493]
from pathlib import Path

import torch
from torch import nn


class 속담_LSTM(nn.Module):                         # 앞 예제와 같은 구조
    def __init__(self, 글자_수: int, 임베딩_크기: int = 32, 메모_크기: int = 128) -> None:
        super().__init__()
        self.임베딩 = nn.Embedding(글자_수, 임베딩_크기)
        self.lstm = nn.LSTM(임베딩_크기, 메모_크기, batch_first=True)
        self.다음_글자 = nn.Linear(메모_크기, 글자_수)

    def forward(self, x: torch.Tensor, 상태: tuple | None = None) -> tuple[torch.Tensor, tuple]:
        출력, 상태 = self.lstm(self.임베딩(x), 상태)
        return self.다음_글자(출력), 상태


저장본 = torch.load("속담_lstm.pt")
글자들 = 저장본["글자들"]
번호 = {글자: i for i, 글자 in enumerate(글자들)}
모델 = 속담_LSTM(len(글자들))
모델.load_state_dict(저장본["가중치"])
모델.eval()


def 짓기(시작: str, g: torch.Generator, 최대: int = 40) -> str:
    x, 상태, 결과 = torch.tensor([[번호[c] for c in 시작]]), None, 시작
    with torch.no_grad():
        for _ in range(최대):
            점수, 상태 = 모델(x, 상태)
            다음 = torch.multinomial(점수[0, -1].softmax(dim=0), 1, generator=g).item()
            if 글자들[다음] == "\n":
                break
            결과 += 글자들[다음]
            x = torch.tensor([[다음]])
    return 결과.strip()


원래_속담 = set(Path("data/속담.txt").read_text(encoding="utf-8").splitlines())
g = torch.Generator().manual_seed(1)
지은_것 = [짓기("\n", g) for _ in range(30)]        # 줄바꿈 다음, 즉 속담의 첫 글자부터 짓는다
새것 = [s for s in 지은_것 if s not in 원래_속담]
print(f"30개 중 원래 있던 속담 {30 - len(새것)}개, 새로 지은 것 {len(새것)}개")
for s in dict.fromkeys(새것):                     # 겹치는 것은 한 번만
    print(" -", s)

print("시작 글자를 정해 주면:")
for 시작 in ["원숭이", "고양이", "티끌", "사람"]:
    print(" -", " / ".join(짓기(시작, g) for _ in range(3)))
