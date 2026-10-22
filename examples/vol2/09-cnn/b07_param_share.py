# [2권 Chapter 9. CNN과 이미지 분류: 돋보기를 옮기며 무늬 찾기 · 9.3 채널: 겹겹이 쌓인 그림 · manuscript-vol2/chapters/09-cnn.md:315]
import torch
from torch import nn

# 28×28 사진 → 28×28 지도 32장을 만드는 두 방법
합성곱 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
완전연결 = nn.Linear(28 * 28, 32 * 28 * 28)
for 이름, 층 in [("합성곱", 합성곱), ("완전 연결", 완전연결)]:
    print(f"{이름:6} 파라미터 {sum(p.numel() for p in 층.parameters()):>12,}개")

# 1×1 합성곱: 자리마다 채널만 섞는 작은 완전 연결층
torch.manual_seed(0)
x = torch.randn(2, 64, 7, 7)                     # 2장, 채널 64, 7×7
일대일 = nn.Conv2d(64, 16, kernel_size=1)
print("1×1 합성곱:", x.shape, "→", 일대일(x).shape, "파라미터", sum(p.numel() for p in 일대일.parameters()))

선형 = nn.Linear(64, 16)
with torch.no_grad():
    선형.weight.copy_(일대일.weight.reshape(16, 64))
    선형.bias.copy_(일대일.bias)
자리마다 = 선형(x.permute(0, 2, 3, 1)).permute(0, 3, 1, 2)   # 채널을 맨 뒤로 보내 Linear, 다시 제자리
print("자리마다 Linear와 같은가?", torch.allclose(일대일(x), 자리마다, atol=1e-6))
