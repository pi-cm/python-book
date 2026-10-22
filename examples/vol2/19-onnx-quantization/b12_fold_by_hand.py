# [2권 Chapter 19. 모델 내보내기와 경량화: ONNX와 양자화 · 19.6 그래프 들여다보기 · manuscript-vol2/chapters/19-onnx-quantization.md:645]
import torch
import torch.nn.functional as F

from 배포도구 import 불러오기, 작은_ResNet

모델 = 불러오기(작은_ResNet, "fashion_resnet.pt")
합성곱, 정규화 = 모델[0], 모델[1]                    # 첫 Conv2d(1→32)와 BatchNorm2d(32)

# 평가 모드의 배치 정규화: (x - 평균) / sqrt(분산 + eps) * 감마 + 베타 → 채널마다 곱하고 더하기
배율 = 정규화.weight / torch.sqrt(정규화.running_var + 정규화.eps)       # (32,)
새_가중치 = 합성곱.weight * 배율.view(-1, 1, 1, 1)                       # 출력 채널마다 곱하기
새_편향 = 정규화.bias - 정규화.running_mean * 배율                      # 원래 Conv는 bias=False

x = torch.randn(4, 1, 28, 28)
with torch.no_grad():
    두_단계 = 정규화(합성곱(x))
    한_단계 = F.conv2d(x, 새_가중치, 새_편향, padding=1)
print("합성곱 가중치:", tuple(새_가중치.shape), "편향:", tuple(새_편향.shape))
print("두 결과의 최대 차이:", (두_단계 - 한_단계).abs().max().item())
