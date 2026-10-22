# [2권 Chapter 8. 학습 잘 시키기 · 8.11 손실이 안 줄 때 디버깅 · manuscript-vol2/chapters/08-training-well.md:1148]
import torch
from torch import nn

from 학습도구 import 깊은_모델, 데이터_준비


def 그래디언트_크기_보기(모델: nn.Module) -> None:
    """층마다 가중치 그래디언트의 크기(노름)를 첫 층부터 차례로 출력한다."""
    크기들 = [f"{p.grad.norm().item():.1e}" for 이름, p in 모델.named_parameters()
             if 이름.endswith("weight") and p.grad is not None]
    print("  " + " ".join(크기들))


(X_학습, y_학습), _, _ = 데이터_준비(잡음_비율=0.0)

torch.manual_seed(0)
시그모이드_모델 = 깊은_모델(활성화=nn.Sigmoid)
nn.functional.cross_entropy(시그모이드_모델(X_학습), y_학습).backward()
print("Sigmoid 신경망")
그래디언트_크기_보기(시그모이드_모델)

torch.manual_seed(0)
렐루_모델 = 깊은_모델()
for 층 in 렐루_모델.modules():
    if isinstance(층, nn.Linear):
        nn.init.kaiming_normal_(층.weight, nonlinearity="relu")
nn.functional.cross_entropy(렐루_모델(X_학습), y_학습).backward()
print("ReLU 신경망 (Kaiming 초기화)")
그래디언트_크기_보기(렐루_모델)
