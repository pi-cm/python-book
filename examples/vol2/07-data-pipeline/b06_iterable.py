# [2권 Chapter 7. 데이터 파이프라인: Dataset과 DataLoader · 7.3 DataLoader: 배치로 묶어 나르기 · manuscript-vol2/chapters/07-data-pipeline.md:261]
from collections.abc import Iterator

import torch
from torch.utils.data import DataLoader, IterableDataset


class 주문_흐름(IterableDataset):
    """주문 기록을 처음부터 차례로 흘려보내는 데이터셋 (예제용)."""

    def __init__(self, 주문_수: int) -> None:
        self.주문_수 = 주문_수

    def __iter__(self) -> Iterator[torch.Tensor]:
        for 번호 in range(self.주문_수):   # 실제로는 파일을 한 줄씩 읽는 자리
            yield torch.tensor([번호, 번호 * 1000])


로더 = DataLoader(주문_흐름(7), batch_size=3)
for 배치 in 로더:
    print(배치.tolist())

try:
    DataLoader(주문_흐름(7), batch_size=3, shuffle=True)
except ValueError as e:
    print("오류:", str(e).split(",")[0])
