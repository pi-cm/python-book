# [2권 Chapter 9. CNN과 이미지 분류: 돋보기를 옮기며 무늬 찾기 · 9.4 풀링: 줄여서 요약하기 · manuscript-vol2/chapters/09-cnn.md:354]
import torch
from torch import nn

지도 = torch.tensor([[[[1., 3., 0., 2.],
                       [4., 2., 1., 0.],
                       [0., 1., 5., 6.],
                       [2., 0., 7., 1.]]]])        # (1, 1, 4, 4) 특징 맵
print("최대 풀링:", nn.MaxPool2d(2)(지도)[0, 0].tolist())
print("평균 풀링:", nn.AvgPool2d(2)(지도)[0, 0].tolist())

# 반응 위치가 한 칸 움직여도 같은 칸 안이면 최대 풀링 결과는 그대로
가 = torch.zeros(1, 1, 4, 4); 가[0, 0, 0, 0] = 9.0
나 = torch.zeros(1, 1, 4, 4); 나[0, 0, 1, 1] = 9.0
print("한 칸 움직여도 같은가?", torch.equal(nn.MaxPool2d(2)(가), nn.MaxPool2d(2)(나)))

# 전역 평균 풀링: 크기와 상관없이 채널마다 평균 하나만 남긴다
torch.manual_seed(0)
특징맵 = torch.randn(8, 128, 7, 7)               # 8장, 채널 128, 7×7
전역 = nn.AdaptiveAvgPool2d(1)(특징맵)
print(특징맵.shape, "→", 전역.shape)
print("채널 평균과 같은가?", torch.allclose(전역.flatten(1), 특징맵.mean(dim=(2, 3))))
print("14×14를 넣어도:", nn.AdaptiveAvgPool2d(1)(torch.randn(8, 128, 14, 14)).shape)
