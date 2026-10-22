# [2권 Chapter 9. CNN과 이미지 분류: 돋보기를 옮기며 무늬 찾기 · 9.6 그림을 밀어도 알아볼까요? · manuscript-vol2/chapters/09-cnn.md:672]
import torch
from torch import nn

from 옷도구 import 오른쪽으로_밀기

torch.manual_seed(0)
x = torch.zeros(1, 1, 12, 12)
x[0, 0, 3:8, 2:6] = torch.rand(5, 4)             # 가운데 근처에 무늬 하나
합성곱 = nn.Conv2d(1, 4, kernel_size=3, padding=1)

# 1) 밀고 나서 합성곱 vs 합성곱하고 나서 밀기
먼저_밀기 = 합성곱(오른쪽으로_밀기(x, 2))
나중에_밀기 = 오른쪽으로_밀기(합성곱(x), 2)
안쪽 = (slice(None), slice(None), slice(None), slice(2, None))   # 밀려서 새로 생긴 왼쪽 두 줄은 빼고
print("합성곱은 밀린 만큼 결과도 밀린다:", torch.allclose(먼저_밀기[안쪽], 나중에_밀기[안쪽], atol=1e-6))

# 2) 그런데 한 줄로 펴면 같은 무늬가 전혀 다른 칸에 들어간다
펴기 = nn.Flatten()
원래, 밀린 = 펴기(합성곱(x)), 펴기(합성곱(오른쪽으로_밀기(x, 2)))
print(f"한 줄로 편 뒤 같은 칸끼리의 차이 {(원래 - 밀린).abs().mean():.4f}, 값 자체의 크기 {원래.abs().mean():.4f}")

# 3) 전역 평균 풀링은 자리를 잊고 채널마다 '얼마나 있나'만 남긴다
전역 = nn.AdaptiveAvgPool2d(1)
a, b = 전역(합성곱(x)).flatten(), 전역(합성곱(오른쪽으로_밀기(x, 2))).flatten()
print("전역 평균 풀링 뒤:", [round(v, 4) for v in a.tolist()])
print("밀고 나서      :", [round(v, 4) for v in b.tolist()])
