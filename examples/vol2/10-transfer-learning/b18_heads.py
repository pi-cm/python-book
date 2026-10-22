# [2권 Chapter 10. 전이 학습: 남이 학습한 모델 빌려 쓰기 · 10.7 다른 모델, 다른 입력 · manuscript-vol2/chapters/10-transfer-learning.md:975]
import torch
from torch import nn
from torchvision import models


def 머리_바꾸기(모델: nn.Module, 클래스_수: int) -> str:
    """모델에 등록된 마지막 nn.Linear를 찾아 클래스_수만큼 내는 새 층으로 바꾼다."""
    이름, 마지막 = [(n, m) for n, m in 모델.named_modules() if isinstance(m, nn.Linear)][-1]
    부모_이름, _, 자식_이름 = 이름.rpartition(".")         # "classifier.3" → "classifier", "3"
    setattr(모델.get_submodule(부모_이름), 자식_이름, nn.Linear(마지막.in_features, 클래스_수))
    return 이름


for 이름 in ["resnet18", "mobilenet_v3_small", "efficientnet_b0", "vit_b_16"]:
    모델 = models.get_model(이름, weights=None)            # 구조만 본다
    바꾼_곳 = 머리_바꾸기(모델, 10)
    with torch.no_grad():
        출력 = 모델.eval()(torch.zeros(1, 3, 224, 224))
    print(f"{이름:19} 마지막 층 '{바꾼_곳}' → {모델.get_submodule(바꾼_곳)}, 출력 {tuple(출력.shape)}")
