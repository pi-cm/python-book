# [2권 Chapter 10. 전이 학습: 남이 학습한 모델 빌려 쓰기 · 10.6 미세조정: 몸통까지 조금씩 고치기 · manuscript-vol2/chapters/10-transfer-learning.md:920]
import copy

import torch
from torch import nn
from torchvision import models

from 전이도구 import 로더_만들기, 유로샛_불러오기, 장치_고르기, 정확도, 한_에폭_학습

장치 = 장치_고르기()
학습_사진, 학습_정답 = 유로샛_불러오기("학습", 50)
검증_사진, 검증_정답 = 유로샛_불러오기("검증", 100)
학습_로더 = 로더_만들기(학습_사진, 학습_정답, 증강=True, 섞기=True)

torch.manual_seed(0)
모델 = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
모델.fc = nn.Linear(512, 10)
처음 = copy.deepcopy(모델.state_dict())          # 미세조정 전 가중치를 복사해 둔다
모델.to(장치)
옵티마이저 = torch.optim.Adam(모델.parameters(), lr=1e-4)
for 에폭 in range(8):
    한_에폭_학습(모델, 학습_로더, 옵티마이저, 장치)
print(f"검증 정확도 {정확도(모델, 로더_만들기(검증_사진, 검증_정답), 장치):.1%}")

# 부분마다 가중치가 처음보다 몇 % 바뀌었나: ‖나중 - 처음‖ / ‖처음‖
나중 = {k: v.cpu() for k, v in 모델.state_dict().items()}
for 부분 in ["conv1", "layer1", "layer2", "layer3", "layer4"]:
    이름들 = [k for k in 처음 if k.startswith(부분 + ".") and k.endswith("weight")]
    전 = torch.cat([처음[k].flatten() for k in 이름들])
    후 = torch.cat([나중[k].flatten() for k in 이름들])
    print(f"{부분:7} 변화율 {(후 - 전).norm() / 전.norm():.2%}")
