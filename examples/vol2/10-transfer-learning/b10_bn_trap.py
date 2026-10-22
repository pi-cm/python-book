# [2권 Chapter 10. 전이 학습: 남이 학습한 모델 빌려 쓰기 · 10.4 특징 추출: 눈은 빌리고 판단만 새로 · manuscript-vol2/chapters/10-transfer-learning.md:531]
import torch
from torch import nn
from torchvision import models

from 전이도구 import 로더_만들기, 유로샛_불러오기

모델 = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
모델.requires_grad_(False)                   # 전부 얼렸다
모델.fc = nn.Identity()
사진, 정답 = 유로샛_불러오기("학습", 10)
x, _ = next(iter(로더_만들기(사진, 정답)))

모델.eval()
with torch.no_grad():
    전 = 모델(x)
print("학습 대상 파라미터:", sum(p.numel() for p in 모델.parameters() if p.requires_grad))
print("bn1 기록 평균(전):", [f"{v:.3f}" for v in 모델.bn1.running_mean[:4].tolist()])

모델.train()                                 # 습관대로 train 모드로 몇 배치 돌리면
with torch.no_grad():
    for _ in range(5):
        모델(x)
print("bn1 기록 평균(후):", [f"{v:.3f}" for v in 모델.bn1.running_mean[:4].tolist()])

모델.eval()
with torch.no_grad():
    후 = 모델(x)
유사도 = nn.functional.cosine_similarity(전, 후, dim=1)
print(f"같은 사진의 특징이 바뀌었나? 최대 차이 {(전 - 후).abs().max():.3f}, 코사인 유사도 평균 {유사도.mean():.3f}")

# 해결: train 모드로 돌리더라도 배치 정규화 층만은 평가 모드로 묶어 둔다
def 배치정규화_고정(모델: nn.Module) -> None:
    for 층 in 모델.modules():
        if isinstance(층, nn.BatchNorm2d):
            층.eval()

새모델 = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
새모델.fc = nn.Identity()
새모델.train()
배치정규화_고정(새모델)
with torch.no_grad():
    for _ in range(5):
        새모델(x)
print("고정한 bn1 기록 평균:", [f"{v:.3f}" for v in 새모델.bn1.running_mean[:4].tolist()])
