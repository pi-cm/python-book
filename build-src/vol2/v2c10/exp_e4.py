import torch
from torch import nn
from torchvision import models
from 전이도구 import *
장치 = 장치_고르기()
학습_사진, 학습_정답 = 유로샛_불러오기("학습", 50)
검증_사진, 검증_정답 = 유로샛_불러오기("검증", 100)
학습_로더 = 로더_만들기(학습_사진, 학습_정답, 증강=True, 섞기=True)
검증_로더 = 로더_만들기(검증_사진, 검증_정답)
for fix in [False, True]:
  for aug in [True, False]:
    torch.manual_seed(0)
    모델 = models.resnet18(weights=models.ResNet18_Weights.DEFAULT); 모델.requires_grad_(False); 모델.fc = nn.Linear(512, 10); 모델.to(장치)
    opt = torch.optim.Adam(모델.fc.parameters(), lr=1e-3)
    tl = 로더_만들기(학습_사진, 학습_정답, 증강=aug, 섞기=True)
    acc=[]
    for e in range(8):
        모델.train()
        if fix:
            for m in 모델.modules():
                if isinstance(m, nn.BatchNorm2d): m.eval()
        for x,y in tl:
            x,y=x.to(장치),y.to(장치); opt.zero_grad(); nn.functional.cross_entropy(모델(x),y).backward(); opt.step()
        acc.append(정확도(모델,검증_로더,장치))
    print(fix, aug, [f"{a:.3f}" for a in acc])
