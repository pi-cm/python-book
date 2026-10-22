# [2권 Chapter 7. 데이터 파이프라인: Dataset과 DataLoader · 7.7 collate_fn: 길이가 다른 샘플 묶기 · manuscript-vol2/chapters/07-data-pipeline.md:747]
import torch
from torch.utils.data import DataLoader, Dataset

# 예제용으로 만든 짧은 식당 리뷰와 라벨(1: 좋음, 0: 나쁨)
리뷰들 = [("맛있어요", 1), ("너무 짜요", 0), ("또 오고 싶어요", 1), ("별로", 0),
         ("친절하고 깔끔해요", 1), ("다시는 안 가요", 0), ("최고", 1), ("기다리다 지쳤어요", 0)]


class 리뷰_데이터셋(Dataset):
    """문장을 글자 번호 텐서로 바꿔 돌려준다. 0번은 빈칸 채우기(패딩)용으로 비워 둔다."""

    def __init__(self, 자료: list[tuple[str, int]]) -> None:
        self.자료 = 자료
        글자들 = sorted({글자 for 문장, _ in 자료 for 글자 in 문장})
        self.글자_번호 = {글자: i + 1 for i, 글자 in enumerate(글자들)}

    def __len__(self) -> int:
        return len(self.자료)

    def __getitem__(self, i: int) -> tuple[torch.Tensor, int]:
        문장, 라벨 = self.자료[i]
        return torch.tensor([self.글자_번호[글자] for 글자 in 문장]), 라벨


데이터 = 리뷰_데이터셋(리뷰들)
print("글자 종류:", len(데이터.글자_번호))
for i in range(3):
    번호들, 라벨 = 데이터[i]
    print(f"{리뷰들[i][0]} → {번호들.tolist()}, 라벨 {라벨}")

try:
    next(iter(DataLoader(데이터, batch_size=4)))
except RuntimeError as e:
    print("오류:", e)
