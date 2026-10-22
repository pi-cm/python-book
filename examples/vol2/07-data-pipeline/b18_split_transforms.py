# [2권 Chapter 7. 데이터 파이프라인: Dataset과 DataLoader · 7.8 학습/검증 나누기: random_split과 재현 가능한 분할 · manuscript-vol2/chapters/07-data-pipeline.md:949]
from collections.abc import Callable

import torch
from torch.utils.data import Dataset, Subset, random_split


class 숫자_데이터셋(Dataset):
    """꺼낼 때 transform을 적용하는 아주 작은 데이터셋 (예제용)."""

    def __init__(self, transform: Callable[[torch.Tensor], torch.Tensor] | None = None) -> None:
        self.X = torch.arange(10).float()
        self.transform = transform

    def __len__(self) -> int:
        return len(self.X)

    def __getitem__(self, i: int) -> torch.Tensor:
        x = self.X[i]
        return self.transform(x) if self.transform else x


def 흔들기(x: torch.Tensor) -> torch.Tensor:
    """학습용 증강 흉내: 작은 잡음을 더한다."""
    return x + torch.randn(()) * 0.1


torch.manual_seed(0)
g = torch.Generator().manual_seed(42)

# 잘못된 방법: 하나를 나누면 검증 쪽도 같은 transform을 쓴다
학습, 검증 = random_split(숫자_데이터셋(transform=흔들기), [0.7, 0.3], generator=g)
print("잘못: 검증 0번을 두 번 꺼내면", round(검증[0].item(), 4), round(검증[0].item(), 4))

# 바른 방법: transform이 다른 두 데이터셋을 만들고, 같은 번호로 나눈다
번호 = torch.randperm(10, generator=g).tolist()
학습 = Subset(숫자_데이터셋(transform=흔들기), 번호[:7])
검증 = Subset(숫자_데이터셋(transform=None), 번호[7:])
print("바름: 검증 0번을 두 번 꺼내면", 검증[0].item(), 검증[0].item())
print("학습 0번을 두 번 꺼내면", round(학습[0].item(), 4), round(학습[0].item(), 4))
