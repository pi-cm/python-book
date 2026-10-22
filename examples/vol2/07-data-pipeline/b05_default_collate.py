# [2권 Chapter 7. 데이터 파이프라인: Dataset과 DataLoader · 7.3 DataLoader: 배치로 묶어 나르기 · manuscript-vol2/chapters/07-data-pipeline.md:212]
import torch
from torch.utils.data import DataLoader, Dataset


class 학생_데이터셋(Dataset):
    """샘플 하나를 딕셔너리로 돌려주는 데이터셋 (예제용 점수)."""

    def __init__(self) -> None:
        self.이름 = ["가온", "나래", "다온", "라희", "마루"]
        self.점수 = torch.tensor([[80.0, 70.0], [92.0, 88.0], [75.0, 95.0],
                                 [60.0, 65.0], [88.0, 91.0]])
        self.합격 = [1, 1, 1, 0, 1]

    def __len__(self) -> int:
        return len(self.이름)

    def __getitem__(self, i: int) -> dict:
        return {"이름": self.이름[i], "점수": self.점수[i], "합격": self.합격[i]}


print("샘플 하나:", 학생_데이터셋()[0])
로더 = DataLoader(학생_데이터셋(), batch_size=3)
배치 = next(iter(로더))                     # 첫 배치만 꺼내 보기
for 키, 값 in 배치.items():
    print(f"{키}: {type(값).__name__} {값}")
