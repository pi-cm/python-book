# [2권 Chapter 9. CNN과 이미지 분류: 돋보기를 옮기며 무늬 찾기 · 9.10 실습: 작은 ResNet으로 옷 분류기 다시 만들기 · manuscript-vol2/chapters/09-cnn.md:1274]
import torch
import torch.nn.functional as F
from torch import nn
from torch.utils.data import DataLoader, Subset
from torchvision import datasets
from torchvision.transforms import v2

from 옷도구 import 시험_데이터, 오른쪽으로_밀기, 장치_고르기


class 잔차블록(nn.Module):
    """9.8절의 잔차 블록."""

    def __init__(self, 입력: int, 출력: int, 보폭: int = 1) -> None:
        super().__init__()
        self.합성곱1 = nn.Conv2d(입력, 출력, 3, stride=보폭, padding=1, bias=False)
        self.정규화1 = nn.BatchNorm2d(출력)
        self.합성곱2 = nn.Conv2d(출력, 출력, 3, padding=1, bias=False)
        self.정규화2 = nn.BatchNorm2d(출력)
        if 보폭 != 1 or 입력 != 출력:
            self.지름길 = nn.Sequential(nn.Conv2d(입력, 출력, 1, stride=보폭, bias=False),
                                        nn.BatchNorm2d(출력))
        else:
            self.지름길 = nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        고칠양 = self.정규화2(self.합성곱2(F.relu(self.정규화1(self.합성곱1(x)))))
        return F.relu(고칠양 + self.지름길(x))


def 작은_ResNet() -> nn.Sequential:
    """28×28 → 28×28(32채널) → 14×14(64채널) → 7×7(128채널) → 전역 평균 풀링 → 10개 점수."""
    return nn.Sequential(
        nn.Conv2d(1, 32, 3, padding=1, bias=False), nn.BatchNorm2d(32), nn.ReLU(),
        잔차블록(32, 32), 잔차블록(32, 64, 보폭=2), 잔차블록(64, 128, 보폭=2),
        nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Dropout(0.3), nn.Linear(128, 10),
    )


@torch.no_grad()
def 정확도_재기(모델: nn.Module, 로더: DataLoader, 장치: torch.device) -> float:
    """로더의 모든 사진에 대한 정확도."""
    모델.eval()
    맞힘 = sum((모델(x.to(장치)).argmax(dim=1).cpu() == y).sum().item() for x, y in 로더)
    return 맞힘 / len(로더.dataset)


기본 = [v2.ToImage(), v2.ToDtype(torch.float32, scale=True)]
증강 = v2.Compose([v2.ToImage(), v2.RandomCrop(28, padding=2),        # 상하좌우 2칸 안에서 무작위로 밀기
                  v2.RandomHorizontalFlip(), v2.ToDtype(torch.float32, scale=True)])
학습용 = datasets.FashionMNIST("data", train=True, download=True, transform=증강)
검증용 = datasets.FashionMNIST("data", train=True, download=True, transform=v2.Compose(기본))
순서 = torch.randperm(60000, generator=torch.Generator().manual_seed(0))
학습셋, 검증셋 = Subset(학습용, 순서[:55000]), Subset(검증용, 순서[55000:])   # 7장 7.8절의 방법

torch.manual_seed(0)
장치 = 장치_고르기()
학습_로더 = DataLoader(학습셋, batch_size=128, shuffle=True)
검증_로더 = DataLoader(검증셋, batch_size=1000)
모델 = 작은_ResNet().to(장치)
에폭수 = 12
옵티마이저 = torch.optim.AdamW(모델.parameters(), lr=2e-3, weight_decay=5e-4)
스케줄러 = torch.optim.lr_scheduler.OneCycleLR(옵티마이저, max_lr=3e-3, total_steps=에폭수 * len(학습_로더))
print(f"장치 {장치}, 파라미터 {sum(p.numel() for p in 모델.parameters()):,}개")

for 에폭 in range(1, 에폭수 + 1):
    모델.train()
    for x, y in 학습_로더:
        x, y = x.to(장치), y.to(장치)
        옵티마이저.zero_grad()
        F.cross_entropy(모델(x), y).backward()
        옵티마이저.step()
        스케줄러.step()                              # OneCycleLR은 배치마다 (8장 8.7절)
    if 에폭 % 3 == 0:
        print(f"에폭 {에폭:2}: 검증 정확도 {정확도_재기(모델, 검증_로더, 장치):.2%}")

torch.save(모델.state_dict(), "fashion_resnet.pt")

# 설계를 모두 마친 뒤 처음으로 시험 데이터를 연다
X, y = 시험_데이터()
이름 = ["T셔츠", "바지", "풀오버", "드레스", "코트", "샌들", "셔츠", "운동화", "가방", "앵클부츠"]
모델.eval()
with torch.no_grad():
    예측 = 모델(X.to(장치)).argmax(dim=1).cpu()
    밀기 = [(모델(오른쪽으로_밀기(X, 칸).to(장치)).argmax(dim=1).cpu() == y).float().mean().item()
            for 칸 in range(5)]
print(f"시험 정확도 {(예측 == y).float().mean():.2%}")
print("상의 네 종류:", ", ".join(f"{이름[k]} {(예측[y == k] == k).float().mean():.1%}" for k in (0, 2, 4, 6)))
print("밀기 0~4칸:", "  ".join(f"{a:.1%}" for a in 밀기))
