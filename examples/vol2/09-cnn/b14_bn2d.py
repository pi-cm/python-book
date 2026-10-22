# [2권 Chapter 9. CNN과 이미지 분류: 돋보기를 옮기며 무늬 찾기 · 9.7 CNN 속의 배치 정규화와 드롭아웃 · manuscript-vol2/chapters/09-cnn.md:723]
import torch
from torch import nn

torch.manual_seed(0)
x = torch.randn(16, 3, 8, 8) * 5 + 2             # 16장, 채널 3, 8×8. 일부러 눈금을 크게
bn = nn.BatchNorm2d(3)                           # 채널 3개짜리 배치 정규화
print("학습할 숫자:", [tuple(p.shape) for p in bn.parameters()])

bn.train()
출력 = bn(x)
# 채널마다 (장 수, 세로, 가로) 전체에서 평균·분산을 낸다
평균 = x.mean(dim=(0, 2, 3), keepdim=True)
분산 = x.var(dim=(0, 2, 3), keepdim=True, unbiased=False)
print("손으로 계산과 같은가?", torch.allclose(출력, (x - 평균) / torch.sqrt(분산 + bn.eps), atol=1e-5))
print("채널별 평균:", [round(v, 4) + 0.0 for v in 출력.mean(dim=(0, 2, 3)).tolist()])
print("채널별 표준편차:", [round(v, 4) for v in 출력.std(dim=(0, 2, 3), unbiased=False).tolist()])

# 합성곱의 편향은 배치 정규화가 평균을 빼면서 지워 버린다
torch.manual_seed(1)
편향있음 = nn.Conv2d(3, 4, kernel_size=3, padding=1, bias=True)
편향없음 = nn.Conv2d(3, 4, kernel_size=3, padding=1, bias=False)
with torch.no_grad():
    편향없음.weight.copy_(편향있음.weight)
bn4 = nn.BatchNorm2d(4)
print("편향이 있으나 없으나 같은가?", torch.allclose(bn4(편향있음(x)), bn4(편향없음(x)), atol=1e-5))
