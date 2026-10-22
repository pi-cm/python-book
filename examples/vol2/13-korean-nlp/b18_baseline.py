# [2권 Chapter 13. 한국어 NLP 실전: 토크나이저부터 감성 분류까지 · 13.8 처음부터 학습하는 기준 모델 · manuscript-vol2/chapters/13-korean-nlp.md:718]
import torch
from tokenizers import Tokenizer, models, pre_tokenizers, trainers
from torch import nn
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader

from 한국어도구 import NSMC_읽기

전체 = NSMC_읽기("ratings_train.txt")
시험 = NSMC_읽기("ratings_test.txt", 5000)

토크나이저 = Tokenizer(models.BPE(unk_token="[UNK]"))
토크나이저.pre_tokenizer = pre_tokenizers.Whitespace()
토크나이저.train_from_iterator([s for s, _ in 전체], trainers.BpeTrainer(
    vocab_size=8000, special_tokens=["[PAD]", "[UNK]"], show_progress=False))


class 평균_임베딩_분류기(nn.Module):
    """토큰 화살표들의 평균 하나로 긍정/부정을 가린다. 순서는 보지 않는다."""

    def __init__(self, 사전_크기: int, 칸수: int = 64) -> None:
        super().__init__()
        self.임베딩 = nn.Embedding(사전_크기, 칸수, padding_idx=0)
        self.출력 = nn.Linear(칸수, 2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        마스크 = (x != 0).unsqueeze(-1).float()                     # 패딩(0번)은 평균에서 뺀다
        평균 = (self.임베딩(x) * 마스크).sum(1) / 마스크.sum(1).clamp(min=1)
        return self.출력(평균)


def 묶기(배치: list[tuple[str, int]]) -> tuple[torch.Tensor, torch.Tensor]:
    번호들 = [torch.tensor(토크나이저.encode(s).ids[:64]) for s, _ in 배치]
    return pad_sequence(번호들, batch_first=True), torch.tensor([y for _, y in 배치])


def 학습하고_평가(학습: list[tuple[str, int]], 에폭: int = 3) -> 평균_임베딩_분류기:
    torch.manual_seed(0)
    모델 = 평균_임베딩_분류기(토크나이저.get_vocab_size())
    옵티마이저 = torch.optim.Adam(모델.parameters(), lr=3e-3)
    로더 = DataLoader(학습, batch_size=64, shuffle=True, collate_fn=묶기,
                      generator=torch.Generator().manual_seed(0))
    for _ in range(에폭):
        모델.train()
        for x, y in 로더:
            옵티마이저.zero_grad()
            nn.functional.cross_entropy(모델(x), y).backward()
            옵티마이저.step()
    모델.eval()
    with torch.no_grad():
        x, y = 묶기(시험)
        정확도 = (모델(x).argmax(1) == y).float().mean().item()
    print(f"학습 {len(학습):>7,}개 → 시험 정확도 {정확도:.4f}")
    return 모델


학습하고_평가(전체[:5000])
학습하고_평가(전체[:20000])
모델 = 학습하고_평가(전체)

# 임베딩이 배운 '긍정 쪽 방향': 출력층의 (긍정 가중치 - 부정 가중치)
방향 = 모델.출력.weight[1] - 모델.출력.weight[0]
점수 = (모델.임베딩.weight @ 방향).detach()
번호_토큰 = {i: t for t, i in 토크나이저.get_vocab().items()}
print("긍정 쪽 끝:", [번호_토큰[i] for i in 점수.topk(8).indices.tolist()])
print("부정 쪽 끝:", [번호_토큰[i] for i in (-점수).topk(8).indices.tolist()])
