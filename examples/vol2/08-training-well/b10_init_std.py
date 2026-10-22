# [2권 Chapter 8. 학습 잘 시키기 · 8.6 가중치 초기화 · manuscript-vol2/chapters/08-training-well.md:569]
import torch
from torch import nn

torch.manual_seed(0)
x = torch.randn(512, 256)                     # 입력: 평균 0, 표준편차 1


def 층별_표준편차(초기화) -> str:
    """ReLU 층 10개를 통과하며 출력의 표준편차가 어떻게 변하는지 잰다."""
    h = x
    결과 = []
    for 층 in range(1, 11):
        선형 = nn.Linear(256, 256, bias=False)
        초기화(선형.weight)
        h = torch.relu(선형(h))
        if 층 in (1, 2, 5, 10):
            결과.append(f"{층}층 {h.std().item():.2e}")
    return ", ".join(결과)


with torch.no_grad():
    print("표준편차 0.01:", 층별_표준편차(lambda w: nn.init.normal_(w, std=0.01)))
    print("표준편차 1.0 :", 층별_표준편차(lambda w: nn.init.normal_(w, std=1.0)))
    print("Kaiming      :", 층별_표준편차(lambda w: nn.init.kaiming_normal_(w, nonlinearity="relu")))
