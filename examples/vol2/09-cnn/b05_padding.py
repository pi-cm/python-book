# [2권 Chapter 9. CNN과 이미지 분류: 돋보기를 옮기며 무늬 찾기 · 9.2 패딩과 보폭: 출력 크기 정하기 · manuscript-vol2/chapters/09-cnn.md:220]
import torch
import torch.nn.functional as F
from torch import nn


def 출력_크기(n: int, k: int, p: int = 0, s: int = 1) -> int:
    """입력 n, 필터 k, 패딩 p, 보폭 s일 때 합성곱 출력의 한 변 길이."""
    return (n + 2 * p - k) // s + 1


# 패딩: 테두리에 0을 한 칸 두르기
작은그림 = torch.ones(1, 1, 3, 3)
print(F.pad(작은그림, (1, 1, 1, 1))[0, 0])           # (왼, 오른, 위, 아래)로 한 칸씩

x = torch.zeros(1, 1, 28, 28)                         # 옷 사진 한 장 크기
설정들 = [dict(kernel_size=3), dict(kernel_size=3, padding=1), dict(kernel_size=5),
          dict(kernel_size=5, padding=2), dict(kernel_size=3, stride=2, padding=1),
          dict(kernel_size=2, stride=2), dict(kernel_size=3, padding="same")]
for 설정 in 설정들:
    실제 = nn.Conv2d(1, 1, **설정)(x).shape[-1]
    k, s = 설정["kernel_size"], 설정.get("stride", 1)
    p = (k - 1) // 2 if 설정.get("padding") == "same" else 설정.get("padding", 0)
    print(f"{str(설정):45} → {실제}×{실제}  (공식: {출력_크기(28, k, p, s)})")
