# [2권 Chapter 10. 전이 학습: 남이 학습한 모델 빌려 쓰기 · 10.4 특징 추출: 눈은 빌리고 판단만 새로 · manuscript-vol2/chapters/10-transfer-learning.md:477]
import torch
from torch import nn
from torchvision import models

from 전이도구 import 로더_만들기, 유로샛_불러오기, 장치_고르기, 특징_뽑기

장치 = 장치_고르기()
몸통 = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
몸통.fc = nn.Identity()                   # 마지막 층을 "그대로 통과"로 바꾸면 특징 추출기
몸통.requires_grad_(False)
몸통.to(장치)

학습_사진, 학습_정답 = 유로샛_불러오기("학습", 50)
검증_사진, 검증_정답 = 유로샛_불러오기("검증", 100)
학습_특징, 학습_정답 = 특징_뽑기(몸통, 로더_만들기(학습_사진, 학습_정답), 장치)
검증_특징, 검증_정답 = 특징_뽑기(몸통, 로더_만들기(검증_사진, 검증_정답), 장치)
print("특징:", tuple(학습_특징.shape), tuple(검증_특징.shape))

# 이제 학습은 특징 512개 → 10클래스, 층 하나뿐이다
torch.manual_seed(0)
머리 = nn.Linear(512, 10)
옵티마이저 = torch.optim.Adam(머리.parameters(), lr=1e-3)
for 에폭 in range(1, 101):
    옵티마이저.zero_grad()
    손실 = nn.functional.cross_entropy(머리(학습_특징), 학습_정답)
    손실.backward()
    옵티마이저.step()
    if 에폭 in (1, 10, 25, 50, 100):
        with torch.no_grad():
            학습_정확도 = (머리(학습_특징).argmax(1) == 학습_정답).float().mean()
            검증_정확도 = (머리(검증_특징).argmax(1) == 검증_정답).float().mean()
        print(f"에폭 {에폭:3}: 손실 {손실.item():.4f}, 학습 {학습_정확도:.1%}, 검증 {검증_정확도:.1%}")
