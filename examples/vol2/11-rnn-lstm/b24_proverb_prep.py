# [2권 Chapter 11. RNN과 LSTM: 순서가 있는 데이터 · 11.11 실습: 속담 짓는 글자 단위 LSTM · manuscript-vol2/chapters/11-rnn-lstm.md:1356]
from pathlib import Path

import torch
from torch import nn

글 = Path("data/속담.txt").read_text(encoding="utf-8")
글자들 = sorted(set(글))                            # 줄바꿈 "\n"도 한 글자로 친다
번호 = {글자: i for i, 글자 in enumerate(글자들)}
print("글자 종류:", len(글자들), "앞쪽 다섯:", 글자들[:5])

전체 = torch.tensor([번호[글자] for 글자 in 글])   # 글 전체를 번호 한 줄로
print("번호로 바꾼 글:", tuple(전체.shape), 전체[:8].tolist())

# 다음 글자 맞히기: 입력을 한 칸 밀면 정답이 된다
조각 = 전체[:9]
입력, 정답 = 조각[:-1], 조각[1:]
print("입력:", "".join(글자들[i] for i in 입력))
print("정답:", "".join(글자들[i] for i in 정답))

# nn.Embedding: 번호를 받아 그 번호 줄의 벡터를 꺼내 주는 표
torch.manual_seed(0)
임베딩 = nn.Embedding(len(글자들), 8)             # 글자마다 숫자 8개짜리 벡터
벡터 = 임베딩(입력)
print("임베딩 표:", tuple(임베딩.weight.shape), "→ 꺼낸 벡터:", tuple(벡터.shape))
원핫 = nn.functional.one_hot(입력, len(글자들)).float()
print("원-핫 @ 표와 같은가?", torch.allclose(벡터, 원핫 @ 임베딩.weight))
