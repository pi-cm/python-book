# [2권 Chapter 9. CNN과 이미지 분류: 돋보기를 옮기며 무늬 찾기 · 9.8 유명한 구조의 아이디어 · manuscript-vol2/chapters/09-cnn.md:965]
import torch
import torch.nn.functional as F
from torch import nn


class 블록(nn.Module):
    """합성곱 두 번. 잔차=True면 입력을 더해 내보낸다 (비교를 위해 배치 정규화는 뺐다)."""

    def __init__(self, c: int, 잔차: bool) -> None:
        super().__init__()
        self.잔차 = 잔차
        self.합성곱1 = nn.Conv2d(c, c, 3, padding=1)
        self.합성곱2 = nn.Conv2d(c, c, 3, padding=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        출력 = self.합성곱2(F.relu(self.합성곱1(x)))
        return F.relu(출력 + x) if self.잔차 else F.relu(출력)


def 깊은_CNN(블록수: int, 잔차: bool) -> nn.Sequential:
    """첫 합성곱 + 블록 여러 개 + 전역 평균 풀링 + 분류층."""
    return nn.Sequential(nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(),
                         *[블록(16, 잔차) for _ in range(블록수)],
                         nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(16, 10))


torch.manual_seed(0)
x = torch.randn(32, 1, 14, 14)                   # 예제용 무작위 입력과 정답
y = torch.randint(0, 10, (32,))
print("합성곱층 수   평범한 CNN   잔차 CNN   (첫 층 기울기 크기)")
for 블록수 in (2, 10, 25):
    크기 = []
    for 잔차 in (False, True):
        torch.manual_seed(0)
        모델 = 깊은_CNN(블록수, 잔차)
        F.cross_entropy(모델(x), y).backward()
        크기.append(모델[0].weight.grad.norm().item())
    print(f"{블록수 * 2 + 1:>8}     {크기[0]:10.2e}   {크기[1]:9.2e}")
