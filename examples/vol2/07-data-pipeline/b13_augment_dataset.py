# [2권 Chapter 7. 데이터 파이프라인: Dataset과 DataLoader · 7.6 transforms: 꺼낼 때 손질하기 · manuscript-vol2/chapters/07-data-pipeline.md:684]
import torch
from torch.utils.data import Dataset
from torchvision.transforms import v2

ㄱ = torch.tensor([[0, 0, 0, 0, 0, 0],
                  [0, 1, 1, 1, 1, 0],
                  [0, 0, 0, 0, 1, 0],
                  [0, 0, 0, 0, 1, 0],
                  [0, 0, 0, 0, 1, 0],
                  [0, 0, 0, 0, 0, 0]], dtype=torch.uint8).unsqueeze(0)   # (1, 6, 6)


class 글자_데이터셋(Dataset):
    """그림 한 장짜리 데이터셋. 꺼낼 때마다 transform을 새로 적용한다."""

    def __init__(self, transform: v2.Transform | None = None) -> None:
        self.그림들 = [ㄱ]
        self.transform = transform

    def __len__(self) -> int:
        return len(self.그림들)

    def __getitem__(self, i: int) -> torch.Tensor:
        그림 = self.그림들[i]
        return self.transform(그림) if self.transform else 그림


def 그려_보기(그림들: list[torch.Tensor]) -> None:
    """여러 그림을 #과 . 으로 나란히 찍는다."""
    for 줄 in range(그림들[0].shape[1]):
        print("   ".join("".join("#" if v else "." for v in g[0, 줄].tolist()) for g in 그림들))


torch.manual_seed(1)
증강 = v2.Compose([v2.RandomHorizontalFlip(p=0.5),
                  v2.RandomCrop(size=6, padding=1)])
데이터 = 글자_데이터셋(transform=증강)
그려_보기([데이터[0] for _ in range(5)])        # 같은 0번 샘플을 다섯 번 꺼낸다
