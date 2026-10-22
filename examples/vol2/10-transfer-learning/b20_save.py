# [2권 Chapter 10. 전이 학습: 남이 학습한 모델 빌려 쓰기 · 10.8 저장하고 불러오기 · manuscript-vol2/chapters/10-transfer-learning.md:1092]
from pathlib import Path

import torch
from torch import nn
from torchvision import models

from 전이도구 import 로더_만들기, 유로샛_불러오기, 머리_학습, 정확도, 특징_뽑기

장치 = torch.device("cpu")
학습_사진, 학습_정답 = 유로샛_불러오기("학습", 50)
검증_사진, 검증_정답 = 유로샛_불러오기("검증", 100)
검증_로더 = 로더_만들기(검증_사진, 검증_정답)

# 10.4절처럼 특징 추출로 머리를 학습해 완성 모델을 만든다
모델 = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
모델.fc = nn.Identity()
학습_특징, _ = 특징_뽑기(모델, 로더_만들기(학습_사진, 학습_정답), 장치)
모델.fc = 머리_학습(학습_특징, 학습_정답)
print(f"완성 모델 검증 정확도 {정확도(모델, 검증_로더, 장치):.1%}")

torch.save(모델.state_dict(), "eurosat_resnet18.pt")      # 모델 전체
torch.save(모델.fc.state_dict(), "eurosat_head.pt")       # 머리만
for 파일 in ["eurosat_resnet18.pt", "eurosat_head.pt"]:
    print(f"{파일:20} {Path(파일).stat().st_size / 1024:10,.1f}KB")

# 불러오기 ①: 설계도를 그대로 만들지 않으면
새모델 = models.resnet18(weights=None)
try:
    새모델.load_state_dict(torch.load("eurosat_resnet18.pt", weights_only=True))
except RuntimeError as e:
    for 줄 in str(e).splitlines()[1:]:
        print("오류:", 줄.strip())

# 불러오기 ②: 머리를 바꾼 설계도에 전체를 채운다
새모델.fc = nn.Linear(512, 10)
새모델.load_state_dict(torch.load("eurosat_resnet18.pt", weights_only=True))
print(f"전체를 불러온 모델 {정확도(새모델, 검증_로더, 장치):.1%}")

# 불러오기 ③: 몸통은 torchvision에서 받고 머리만 채운다
가벼운모델 = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
가벼운모델.fc = nn.Linear(512, 10)
가벼운모델.fc.load_state_dict(torch.load("eurosat_head.pt", weights_only=True))
print(f"머리만 불러온 모델 {정확도(가벼운모델, 검증_로더, 장치):.1%}")
