# [2권 Chapter 9. CNN과 이미지 분류: 돋보기를 옮기며 무늬 찾기 · 9.1 합성곱: 돋보기를 옮기며 무늬 찾기 · manuscript-vol2/chapters/09-cnn.md:111]
import torch
import torch.nn.functional as F
from torch import nn

그림 = torch.tensor([
    [0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0],
], dtype=torch.float32)
필터 = torch.tensor([[-1.0, 2.0, -1.0]] * 3)

# 합성곱 함수는 4차원을 원한다: 그림 (장 수, 채널, 세로, 가로), 필터 (출력 채널, 입력 채널, 세로, 가로)
x = 그림.reshape(1, 1, 6, 6)
w = 필터.reshape(1, 1, 3, 3)
print(x.shape, "*", w.shape, "→", F.conv2d(x, w).shape)
print(F.conv2d(x, w)[0, 0])

# nn.Conv2d는 필터를 파라미터로 품고 있는 층이다
층 = nn.Conv2d(in_channels=1, out_channels=1, kernel_size=3, bias=False)
print("층의 필터 모양:", 층.weight.shape)
with torch.no_grad():
    층.weight.copy_(w)                               # 무작위 필터를 우리 필터로 바꿔 끼우기
print("손 계산과 같은가?", torch.equal(층(x), F.conv2d(x, w)))
