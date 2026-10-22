# [2권 Chapter 9. CNN과 이미지 분류: 돋보기를 옮기며 무늬 찾기 · 9.8 유명한 구조의 아이디어 · manuscript-vol2/chapters/09-cnn.md:909]
import torch
import torch.nn.functional as F
from torch import nn


class 잔차블록(nn.Module):
    """합성곱 두 번으로 '고칠 양'만 배우고, 입력을 그대로 더해 내보내는 블록."""

    def __init__(self, 입력: int, 출력: int, 보폭: int = 1) -> None:
        super().__init__()
        self.합성곱1 = nn.Conv2d(입력, 출력, 3, stride=보폭, padding=1, bias=False)
        self.정규화1 = nn.BatchNorm2d(출력)
        self.합성곱2 = nn.Conv2d(출력, 출력, 3, padding=1, bias=False)
        self.정규화2 = nn.BatchNorm2d(출력)
        # 모양이 달라지면 지름길도 1×1 합성곱으로 모양을 맞춘다
        if 보폭 != 1 or 입력 != 출력:
            self.지름길 = nn.Sequential(nn.Conv2d(입력, 출력, 1, stride=보폭, bias=False),
                                        nn.BatchNorm2d(출력))
        else:
            self.지름길 = nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        고칠양 = self.정규화2(self.합성곱2(F.relu(self.정규화1(self.합성곱1(x)))))
        return F.relu(고칠양 + self.지름길(x))         # 핵심은 이 덧셈 한 번


torch.manual_seed(0)
x = torch.randn(8, 32, 14, 14)
같은크기 = 잔차블록(32, 32)
줄이기 = 잔차블록(32, 64, 보폭=2)
print("같은 크기:", tuple(x.shape), "→", tuple(같은크기(x).shape), type(같은크기.지름길).__name__)
print("줄이기   :", tuple(x.shape), "→", tuple(줄이기(x).shape), type(줄이기.지름길).__name__)

# 고칠 양을 0으로 만들면 블록은 입력을 (ReLU만 거쳐) 그대로 내보낸다
nn.init.zeros_(같은크기.정규화2.weight)
같은크기.eval()
print("고칠 양이 0이면 그대로 통과:", torch.allclose(같은크기(x), F.relu(x)))
