# [2권 Chapter 10. 전이 학습: 남이 학습한 모델 빌려 쓰기 · 10.6 미세조정: 몸통까지 조금씩 고치기 · manuscript-vol2/chapters/10-transfer-learning.md:750]
import torch
from torch import nn
from torchvision import models

from 전이도구 import 로더_만들기, 유로샛_불러오기, 장치_고르기, 정확도, 한_에폭_학습

장치 = 장치_고르기()
학습_사진, 학습_정답 = 유로샛_불러오기("학습", 50)
검증_사진, 검증_정답 = 유로샛_불러오기("검증", 100)
학습_로더 = 로더_만들기(학습_사진, 학습_정답, 증강=True, 섞기=True)
검증_로더 = 로더_만들기(검증_사진, 검증_정답)


def 사전학습_모델(클래스_수: int = 10) -> nn.Module:
    """ImageNet 가중치를 불러오고 마지막 층만 새것으로 바꾼다. 아무것도 얼리지 않는다."""
    모델 = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    모델.fc = nn.Linear(모델.fc.in_features, 클래스_수)
    return 모델


for 학습률 in [1e-2, 1e-3, 1e-4]:
    torch.manual_seed(0)
    모델 = 사전학습_모델().to(장치)
    옵티마이저 = torch.optim.Adam(모델.parameters(), lr=학습률)
    기록 = []
    for 에폭 in range(8):
        한_에폭_학습(모델, 학습_로더, 옵티마이저, 장치)
        기록.append(정확도(모델, 검증_로더, 장치))
    print(f"lr={학습률:g}: 에폭별 검증 정확도", " ".join(f"{a:.0%}" for a in 기록))
