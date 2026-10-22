# [2권 Chapter 9. CNN과 이미지 분류: 돋보기를 옮기며 무늬 찾기 · 9.8 유명한 구조의 아이디어 · manuscript-vol2/chapters/09-cnn.md:782]
import torch
from torch import nn

# LeNet-5 (1998)의 뼈대를 28×28 입력에 맞춘 것. 당시처럼 tanh와 평균 풀링을 쓴다
르넷 = nn.Sequential(
    nn.Conv2d(1, 6, kernel_size=5, padding=2), nn.Tanh(), nn.AvgPool2d(2),   # 28 → 28 → 14
    nn.Conv2d(6, 16, kernel_size=5), nn.Tanh(), nn.AvgPool2d(2),             # 14 → 10 → 5
    nn.Flatten(),
    nn.Linear(16 * 5 * 5, 120), nn.Tanh(),
    nn.Linear(120, 84), nn.Tanh(),
    nn.Linear(84, 10),
)
x = torch.zeros(1, 1, 28, 28)
for 층 in 르넷:
    x = 층(x)
    if not isinstance(층, (nn.Tanh, nn.Flatten)):
        print(f"{type(층).__name__:10} → {tuple(x.shape)}")
print(f"파라미터 {sum(p.numel() for p in 르넷.parameters()):,}개")
