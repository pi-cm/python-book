# [2권 Chapter 6. nn.Module과 학습 루프: 모든 모델이 따르는 표준형 · 6.10 모델 저장과 불러오기 · manuscript-vol2/chapters/06-nn-module.md:986]
import torch
from torch import nn


class 작은신경망(nn.Module):
    """입력 → 은닉층(ReLU) → 출력으로 이어지는 신경망."""

    def __init__(self, 입력수: int, 은닉수: int, 출력수: int) -> None:
        super().__init__()
        self.층1 = nn.Linear(입력수, 은닉수)
        self.활성화 = nn.ReLU()
        self.층2 = nn.Linear(은닉수, 출력수)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.층2(self.활성화(self.층1(x)))


torch.manual_seed(0)
모델 = 작은신경망(4, 8, 3)
상태 = 모델.state_dict()                          # 이름 → 텐서 딕셔너리
for 이름, 값 in 상태.items():
    print(f"{이름:10} {tuple(값.shape)}")
torch.save(상태, "작은신경망.pt")

새_모델 = 작은신경망(4, 8, 3)                      # 같은 설계도로 새로 만들면 숫자가 다르다
x = torch.rand(2, 4)
print("불러오기 전 같은가:", torch.equal(새_모델(x), 모델(x)))
새_모델.load_state_dict(torch.load("작은신경망.pt", weights_only=True))
print("불러온 뒤 같은가  :", torch.equal(새_모델(x), 모델(x)))

다른_모델 = 작은신경망(4, 16, 3)                   # 설계도가 다르면?
try:
    다른_모델.load_state_dict(torch.load("작은신경망.pt", weights_only=True))
except RuntimeError as e:
    print("오류:", str(e).split("\n")[1].strip())
