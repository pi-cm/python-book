# [2권 Chapter 10. 전이 학습: 남이 학습한 모델 빌려 쓰기 · 10.3 이 장의 데이터: EuroSAT 위성 사진 · manuscript-vol2/chapters/10-transfer-learning.md:275]
# 전이도구.py — 10장 예제가 함께 쓰는 준비 코드
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets
from torchvision.transforms import v2

IMAGENET_평균 = [0.485, 0.456, 0.406]      # 사전학습 모델이 배운 기준(10.2절)
IMAGENET_표준편차 = [0.229, 0.224, 0.225]
구간_시작 = {"학습": 0, "검증": 1000, "시험": 1500}   # 클래스마다 섞은 순서에서 겹치지 않는 구간


def 장치_고르기() -> torch.device:
    """쓸 수 있는 가장 빠른 장치를 고른다."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def 유로샛_불러오기(구간: str, 클래스당: int) -> tuple[torch.Tensor, torch.Tensor]:
    """EuroSAT에서 클래스마다 같은 수를 골라 (사진 uint8 텐서, 정답)으로 돌려준다."""
    원본 = datasets.EuroSAT("data", download=True)
    정답들 = torch.tensor(원본.targets)
    번호 = []
    for k in range(len(원본.classes)):
        후보 = (정답들 == k).nonzero().flatten()
        섞기 = torch.randperm(len(후보), generator=torch.Generator().manual_seed(k))
        시작 = 구간_시작[구간]
        번호 += 후보[섞기[시작:시작 + 클래스당]].tolist()
    사진 = torch.stack([v2.functional.pil_to_tensor(원본[i][0]) for i in 번호])
    return 사진, 정답들[번호]


def 변환_만들기(크기: int = 112, 증강: bool = False) -> v2.Compose:
    """크기 맞추기 → (증강) → 0~1 실수 → ImageNet 기준으로 정규화."""
    단계 = [v2.Resize(크기)]
    if 증강:   # 위성 사진은 위아래가 따로 없으니 상하 뒤집기도 정답을 바꾸지 않는다
        단계 += [v2.RandomHorizontalFlip(), v2.RandomVerticalFlip()]
    단계 += [v2.ToDtype(torch.float32, scale=True), v2.Normalize(IMAGENET_평균, IMAGENET_표준편차)]
    return v2.Compose(단계)


class 사진_데이터셋(Dataset):
    """메모리에 올려 둔 사진 텐서를 꺼낼 때마다 변환한다(7장)."""

    def __init__(self, 사진: torch.Tensor, 정답: torch.Tensor, 변환: v2.Compose) -> None:
        self.사진, self.정답, self.변환 = 사진, 정답, 변환

    def __len__(self) -> int:
        return len(self.정답)

    def __getitem__(self, i: int) -> tuple[torch.Tensor, torch.Tensor]:
        return self.변환(self.사진[i]), self.정답[i]


def 로더_만들기(사진: torch.Tensor, 정답: torch.Tensor, 증강: bool = False,
              섞기: bool = False, 크기: int = 112) -> DataLoader:
    """사진 텐서로 DataLoader를 만든다. 섞는 순서는 씨앗으로 고정."""
    데이터셋 = 사진_데이터셋(사진, 정답, 변환_만들기(크기, 증강))
    return DataLoader(데이터셋, batch_size=64, shuffle=섞기,
                      generator=torch.Generator().manual_seed(0))


def 한_에폭_학습(모델: nn.Module, 로더: DataLoader, 옵티마이저: torch.optim.Optimizer,
                장치: torch.device) -> float:
    """한 바퀴 학습하고 평균 손실을 돌려준다(6장)."""
    모델.train()
    합, 개수 = 0.0, 0
    for x, y in 로더:
        x, y = x.to(장치), y.to(장치)
        옵티마이저.zero_grad()
        손실 = nn.functional.cross_entropy(모델(x), y)
        손실.backward()
        옵티마이저.step()
        합, 개수 = 합 + 손실.item() * len(y), 개수 + len(y)
    return 합 / 개수


@torch.no_grad()
def 정확도(모델: nn.Module, 로더: DataLoader, 장치: torch.device) -> float:
    """평가 모드에서 정확도를 잰다."""
    모델.eval()
    맞힘 = sum((모델(x.to(장치)).argmax(1).cpu() == y).sum().item() for x, y in 로더)
    return 맞힘 / len(로더.dataset)


@torch.no_grad()
def 특징_뽑기(몸통: nn.Module, 로더: DataLoader, 장치: torch.device) -> tuple[torch.Tensor, torch.Tensor]:
    """얼린 몸통에 사진을 한 번씩 통과시켜 특징 벡터를 모은다(10.4절)."""
    몸통.eval()
    특징, 정답 = zip(*[(몸통(x.to(장치)).cpu(), y) for x, y in 로더])
    return torch.cat(특징), torch.cat(정답)


def 머리_학습(특징: torch.Tensor, 정답: torch.Tensor, 에폭: int = 100) -> nn.Linear:
    """특징 벡터만으로 마지막 층 하나를 학습한다. 데이터가 작아 한 번에 다 넣는다."""
    torch.manual_seed(0)
    머리 = nn.Linear(특징.shape[1], int(정답.max()) + 1)
    옵티마이저 = torch.optim.Adam(머리.parameters(), lr=1e-3)
    for _ in range(에폭):
        옵티마이저.zero_grad()
        nn.functional.cross_entropy(머리(특징), 정답).backward()
        옵티마이저.step()
    return 머리
