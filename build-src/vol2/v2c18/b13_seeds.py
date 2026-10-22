import os
import statistics

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from torchvision import datasets

데이터_폴더 = os.environ.get("BOOK_DATA_DIR", "data")

학습셋 = datasets.FashionMNIST(데이터_폴더, train=True, download=True)
시험셋 = datasets.FashionMNIST(데이터_폴더, train=False, download=True)
학습_로더 = DataLoader(TensorDataset(학습셋.data.float().unsqueeze(1) / 255, 학습셋.targets),
                    batch_size=64, shuffle=True)
X_시험, y_시험 = 시험셋.data.float().unsqueeze(1) / 255, 시험셋.targets


def 학습하고_재기(옵티마이저_만들기, 씨앗: int, 에폭수: int = 2) -> float:
    """6장 6.11절의 옵티마이저 비교와 같은 실험. 씨앗만 바꿀 수 있게 했다."""
    torch.manual_seed(씨앗)
    모델 = nn.Sequential(nn.Flatten(), nn.Linear(28 * 28, 256), nn.ReLU(),
                         nn.Linear(256, 128), nn.ReLU(), nn.Linear(128, 10))
    옵티마이저 = 옵티마이저_만들기(모델.parameters())
    for _ in range(에폭수):
        for x, y in 학습_로더:
            옵티마이저.zero_grad()
            nn.functional.cross_entropy(모델(x), y).backward()
            옵티마이저.step()
    with torch.no_grad():
        return (모델(X_시험).argmax(dim=1) == y_시험).float().mean().item()


후보 = {
    "Adam lr=0.001": lambda p: torch.optim.Adam(p, lr=0.001),
    "Adam lr=0.002": lambda p: torch.optim.Adam(p, lr=0.002),
    "SGD+momentum ": lambda p: torch.optim.SGD(p, lr=0.01, momentum=0.9),
}
씨앗들 = range(5)
결과 = {이름: [학습하고_재기(만들기, 씨앗) for 씨앗 in 씨앗들] for 이름, 만들기 in 후보.items()}

for 이름, 값들 in 결과.items():
    print(f"{이름}  " + " ".join(f"{v:.2%}" for v in 값들)
          + f"  → 평균 {statistics.mean(값들):.2%} ± {statistics.stdev(값들):.2%}")

# 같은 씨앗끼리 짝지어 차이 보기
for 상대 in ("Adam lr=0.002", "SGD+momentum "):
    차이 = [(a - b) * 100 for a, b in zip(결과["Adam lr=0.001"], 결과[상대])]     # %p 단위
    평균, 표준편차 = statistics.mean(차이), statistics.stdev(차이)
    표준오차 = 표준편차 / len(차이) ** 0.5            # 평균이 흔들리는 정도
    print(f"Adam lr=0.001 - {상대.strip()}: " + " ".join(f"{d:+.2f}" for d in 차이))
    print(f"  평균 {평균:+.2f}%p, 표준편차 {표준편차:.2f}%p, 표준오차 {표준오차:.2f}%p, "
          f"평균 ÷ 표준오차 = {평균 / 표준오차:.1f}")
