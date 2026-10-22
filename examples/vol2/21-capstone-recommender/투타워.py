# [2권 Chapter 21. 종합 프로젝트: 맛집 추천 AI · 21.8 특징을 함께 쓰는 투-타워 모델 · manuscript-vol2/chapters/21-capstone-recommender.md:820]
"""21장 투-타워 모델: 사용자 탑과 식당 탑이 각자 번호와 특징으로 벡터를 만든다."""
import pandas as pd
import torch
from torch import nn

from 맛집데이터 import 음식들, 지역들
from 추천학습 import 내적추천


class 투타워(내적추천):
    def __init__(self, 사용자: pd.DataFrame, 식당: pd.DataFrame, 차원: int = 32,
                 번호_가리기: float = 0.3) -> None:
        super().__init__()
        self.식당_수, self.번호_가리기 = len(식당), 번호_가리기
        self.모르는_사용자, self.모르는_식당 = len(사용자), len(식당)     # 맨 끝 번호 = '처음 보는'
        # 모델이 볼 수 있는 특징: 사용자는 동네, 식당은 지역·음식·가격대 (숨은_ 열은 쓰지 않는다)
        self.register_buffer("동네", torch.tensor(사용자["동네"].to_numpy()))
        self.register_buffer("식당_특징", torch.tensor(식당[["지역", "음식", "가격대"]].to_numpy()))
        self.사용자_번호 = nn.Embedding(len(사용자) + 1, 차원)
        self.식당_번호 = nn.Embedding(len(식당) + 1, 차원)
        self.동네_표 = nn.Embedding(len(지역들), 차원)
        self.지역_표 = nn.Embedding(len(지역들), 차원)
        self.음식_표 = nn.Embedding(len(음식들), 차원)
        self.가격_표 = nn.Embedding(4, 차원)
        self.사용자_탑 = nn.Sequential(nn.Linear(2 * 차원, 2 * 차원), nn.ReLU(), nn.Linear(2 * 차원, 차원))
        self.식당_탑 = nn.Sequential(nn.Linear(4 * 차원, 2 * 차원), nn.ReLU(), nn.Linear(2 * 차원, 차원))

    def 가리기(self, 번호: torch.Tensor, 모르는_번호: int) -> torch.Tensor:
        """학습 중에는 일부 번호를 '처음 보는' 번호로 바꿔, 특징만으로도 맞히게 훈련한다."""
        if not self.training:
            return 번호
        return torch.where(torch.rand(번호.shape) < self.번호_가리기, 모르는_번호, 번호)

    def 사용자_벡터(self, 사용자: torch.Tensor, 번호_쓰기: bool = True) -> torch.Tensor:
        번호 = self.가리기(사용자, self.모르는_사용자) if 번호_쓰기 else torch.full_like(사용자, self.모르는_사용자)
        return self.사용자_탑(torch.cat([self.사용자_번호(번호), self.동네_표(self.동네[사용자])], dim=-1))

    def 식당_벡터(self, 식당: torch.Tensor, 번호_쓰기: bool = True) -> torch.Tensor:
        번호 = self.가리기(식당, self.모르는_식당) if 번호_쓰기 else torch.full_like(식당, self.모르는_식당)
        지역, 음식, 가격 = self.식당_특징[식당].unbind(dim=-1)
        return self.식당_탑(torch.cat([self.식당_번호(번호), self.지역_표(지역),
                                     self.음식_표(음식), self.가격_표(가격)], dim=-1))
