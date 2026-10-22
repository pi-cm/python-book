"""21장 추천 모델 학습 도구: 행렬 분해 모델, 음성 샘플링, BCE·BPR 손실, 학습 루프."""
import copy
from collections.abc import Callable
from dataclasses import dataclass

import pandas as pd
import torch
from torch import nn

from 순위지표 import 좋은_평점


@dataclass(frozen=True)
class 학습설정:
    손실: str = "bpr"           # "bce" 또는 "bpr"
    차원: int = 32
    에폭: int = 50
    배치_크기: int = 1024
    학습률: float = 0.005
    가중치_감쇠: float = 1e-4
    씨앗: int = 0


class 내적추천(nn.Module):
    """점수 = 사용자 벡터 · 식당 벡터. 행렬 분해와 투-타워가 함께 쓰는 틀."""

    def forward(self, 사용자: torch.Tensor, 식당: torch.Tensor) -> torch.Tensor:
        return (self.사용자_벡터(사용자) * self.식당_벡터(식당)).sum(dim=-1)

    def 모든_점수(self, 사용자: torch.Tensor) -> torch.Tensor:
        """사용자들 × 모든 식당의 점수표."""
        return self.사용자_벡터(사용자) @ self.식당_벡터(torch.arange(self.식당_수)).T


class 행렬분해(내적추천):
    def __init__(self, 사용자_수: int, 식당_수: int, 차원: int = 32) -> None:
        super().__init__()
        self.식당_수 = 식당_수
        self.사용자 = nn.Embedding(사용자_수, 차원)
        self.식당 = nn.Embedding(식당_수, 차원)
        self.편향 = nn.Embedding(식당_수, 1)            # 식당마다 '누구에게나 끌리는 정도'
        nn.init.normal_(self.사용자.weight, std=0.1)
        nn.init.normal_(self.식당.weight, std=0.1)
        nn.init.zeros_(self.편향.weight)

    def 사용자_벡터(self, 사용자: torch.Tensor) -> torch.Tensor:
        u = self.사용자(사용자)
        return torch.cat([u, torch.ones_like(u[..., :1])], dim=-1)    # 끝에 1을 붙이면

    def 식당_벡터(self, 식당: torch.Tensor) -> torch.Tensor:
        return torch.cat([self.식당(식당), self.편향(식당)], dim=-1)   # 내적에 편향이 더해진다


def 좋았던_쌍(방문: pd.DataFrame) -> torch.Tensor:
    """좋았던 방문을 (사용자, 식당) 짝으로. 같은 곳을 여러 번 가도 한 번만 센다."""
    좋았던 = 방문[방문["평점"] >= 좋은_평점][["사용자", "식당"]].drop_duplicates()
    return torch.tensor(좋았던.to_numpy())


def 손실_계산(모델: 내적추천, 사용자: torch.Tensor, 양성: torch.Tensor,
              음성: torch.Tensor, 종류: str) -> torch.Tensor:
    양성_점수, 음성_점수 = 모델(사용자, 양성), 모델(사용자, 음성)
    if 종류 == "bce":     # 간 곳은 1, 무작위로 뽑은 곳은 0으로 맞히는 분류 문제
        점수 = torch.cat([양성_점수, 음성_점수])
        정답 = torch.cat([torch.ones_like(양성_점수), torch.zeros_like(음성_점수)])
        return nn.functional.binary_cross_entropy_with_logits(점수, 정답)
    # bpr: 간 곳의 점수가 무작위로 뽑은 곳보다 높기만 하면 된다
    return -nn.functional.logsigmoid(양성_점수 - 음성_점수).mean()


def 학습하기(모델: 내적추천, 쌍: torch.Tensor, 후보_식당: torch.Tensor, 설정: 학습설정,
            검증: Callable[[내적추천], float] | None = None) -> list[dict]:
    """미니배치마다 음성 식당을 무작위로 뽑아 학습한다. 검증 점수가 가장 좋던 에폭으로 되돌린다."""
    생성기 = torch.Generator().manual_seed(설정.씨앗)
    옵티마이저 = torch.optim.Adam(모델.parameters(), lr=설정.학습률, weight_decay=설정.가중치_감쇠)
    기록, 최고, 최고_상태 = [], -1.0, None
    for 에폭 in range(1, 설정.에폭 + 1):
        모델.train()
        순서 = torch.randperm(len(쌍), generator=생성기)
        합계 = 0.0
        for 시작 in range(0, len(쌍), 설정.배치_크기):
            u, 양성 = 쌍[순서[시작:시작 + 설정.배치_크기]].T
            음성 = 후보_식당[torch.randint(len(후보_식당), (len(u),), generator=생성기)]
            손실 = 손실_계산(모델, u, 양성, 음성, 설정.손실)
            옵티마이저.zero_grad()
            손실.backward()
            옵티마이저.step()
            합계 += 손실.item() * len(u)
        모델.eval()
        점수 = 검증(모델) if 검증 else float("nan")
        기록.append({"에폭": 에폭, "손실": 합계 / len(쌍), "검증": 점수})
        if 점수 > 최고:
            최고, 최고_상태 = 점수, copy.deepcopy(모델.state_dict())
    if 최고_상태 is not None:
        모델.load_state_dict(최고_상태)          # 조기 종료처럼 가장 좋던 때로 (8장 8.8절)
    return 기록
