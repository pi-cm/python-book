# [2권 Chapter 10. 전이 학습: 남이 학습한 모델 빌려 쓰기 · 10.7 다른 모델, 다른 입력 · manuscript-vol2/chapters/10-transfer-learning.md:1012]
import torch
from torch import nn
from torchvision import models

from 전이도구 import 로더_만들기, 유로샛_불러오기, 장치_고르기, 머리_학습, 특징_뽑기

장치 = 장치_고르기()
학습_사진, 학습_정답 = 유로샛_불러오기("학습", 50)
검증_사진, 검증_정답 = 유로샛_불러오기("검증", 100)

for 이름 in ["mobilenet_v3_small", "resnet18", "efficientnet_b0"]:
    모델 = models.get_model(이름, weights="DEFAULT")          # 처음 한 번은 가중치를 내려받는다
    마지막 = [n for n, m in 모델.named_modules() if isinstance(m, nn.Linear)][-1]
    부모, _, 자식 = 마지막.rpartition(".")
    setattr(모델.get_submodule(부모), 자식, nn.Identity())   # 마지막 층을 떼면 특징 추출기
    모델.to(장치)
    학습_특징, _ = 특징_뽑기(모델, 로더_만들기(학습_사진, 학습_정답), 장치)
    검증_특징, _ = 특징_뽑기(모델, 로더_만들기(검증_사진, 검증_정답), 장치)
    머리 = 머리_학습(학습_특징, 학습_정답)
    with torch.no_grad():
        정확도 = (머리(검증_특징).argmax(1) == 검증_정답).float().mean()
    개수 = sum(p.numel() for p in 모델.parameters())
    print(f"{이름:19} 몸통 {개수 / 1e6:4.1f}백만 개, 특징 {학습_특징.shape[1]:4}개, 검증 정확도 {정확도:.1%}")
