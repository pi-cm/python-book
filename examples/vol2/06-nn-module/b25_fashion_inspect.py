# [2권 Chapter 6. nn.Module과 학습 루프: 모든 모델이 따르는 표준형 · 6.11 실습: FashionMNIST 옷 사진 분류기 · manuscript-vol2/chapters/06-nn-module.md:1251]
import torch
from torch import nn
from torchvision import datasets, transforms

이름 = ["T셔츠", "바지", "풀오버", "드레스", "코트", "샌들", "셔츠", "운동화", "가방", "앵클부츠"]


class 의류분류기(nn.Module):
    """6.11절에서 학습한 모델과 같은 설계도."""

    def __init__(self) -> None:
        super().__init__()
        self.펴기 = nn.Flatten()
        self.층들 = nn.Sequential(
            nn.Linear(28 * 28, 256), nn.ReLU(),
            nn.Linear(256, 128), nn.ReLU(),
            nn.Linear(128, 10),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.층들(self.펴기(x))


모델 = 의류분류기()
모델.load_state_dict(torch.load("fashion_mlp.pt", weights_only=True))
모델.eval()

시험셋 = datasets.FashionMNIST("data", train=False, download=True, transform=transforms.ToTensor())
X = 시험셋.data.float().unsqueeze(1) / 255     # 1만 장을 한 번에: (10000, 1, 28, 28)
y = 시험셋.targets
with torch.no_grad():
    확률 = torch.softmax(모델(X), dim=1)
예측 = 확률.argmax(dim=1)
print(f"전체 정확도: {(예측 == y).float().mean():.2%}")

# 클래스별 정확도
for k in range(10):
    print(f"{이름[k]:6} {(예측[y == k] == k).float().mean():6.1%}", end="   " if k % 2 == 0 else "\n")

# 가장 많이 헷갈린 짝
혼동 = torch.zeros(10, 10, dtype=torch.int64)
for 정답, 답 in zip(y.tolist(), 예측.tolist()):
    혼동[정답, 답] += 1
혼동.fill_diagonal_(0)
for 순위, 위치 in enumerate(혼동.flatten().topk(3).indices.tolist(), start=1):
    정답, 답 = divmod(위치, 10)
    print(f"헷갈림 {순위}위: 정답 {이름[정답]} → 예측 {이름[답]}, {혼동[정답, 답]}번")

# 틀린 사진 세 장: 모델은 얼마나 확신했을까?
for i in (예측 != y).nonzero().flatten()[:3].tolist():
    print(f"{i}번 사진: 정답 {이름[y[i]]}, 예측 {이름[예측[i]]} (확률 {확률[i, 예측[i]]:.1%})")
