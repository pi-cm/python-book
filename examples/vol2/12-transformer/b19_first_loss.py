# [2권 Chapter 12. 어텐션과 트랜스포머: 처음부터 직접 구현 · 12.8 작은 GPT 만들기 · manuscript-vol2/chapters/12-transformer.md:1198]
import math

import torch
from torch.nn import functional as F

from 법전 import 배치_뽑기, 준비
from 작은GPT import 설정, 작은GPT

표, 학습_데이터, _ = 준비()
s = 설정(어휘_크기=len(표))
print(s)
torch.manual_seed(0)
모델 = 작은GPT(s)
for 이름, 부품 in 모델.named_children():
    개수 = sum(p.numel() for p in 부품.parameters())
    if 개수:
        print(f"  {이름}: {개수:,}개")
print(f"모두 {sum(p.numel() for p in 모델.parameters()):,}개")

x, y = 배치_뽑기(학습_데이터, s.문맥_길이, 32, torch.Generator().manual_seed(0))
with torch.no_grad():
    로짓 = 모델(x)
print("입력", tuple(x.shape), "→ 로짓", tuple(로짓.shape))
print(f"학습 전 손실 {F.cross_entropy(로짓.flatten(0, 1), y.flatten()):.4f}, "
      f"찍기 수준 -ln(1/{len(표)}) = {math.log(len(표)):.4f}")
