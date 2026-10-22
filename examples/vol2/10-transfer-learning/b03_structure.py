# [2권 Chapter 10. 전이 학습: 남이 학습한 모델 빌려 쓰기 · 10.1 사전학습 모델 불러오기 · manuscript-vol2/chapters/10-transfer-learning.md:111]
import torch
from torchvision import models

모델 = models.resnet18(weights=None)     # 구조만 볼 때는 가중치를 받지 않아도 된다
x = torch.zeros(1, 3, 224, 224)           # 사진 1장, 3색, 224 × 224
for 이름, 부품 in 모델.named_children():
    if 이름 == "fc":
        x = torch.flatten(x, 1)            # resnet18의 forward가 fc 바로 앞에서 하는 일
    x = 부품(x)
    개수 = sum(p.numel() for p in 부품.parameters())
    print(f"{이름:8} {type(부품).__name__:17} {개수:>10,}개 → {tuple(x.shape)}")
print(모델.fc)
