# [2권 Chapter 8. 학습 잘 시키기 · 8.6 가중치 초기화 · manuscript-vol2/chapters/08-training-well.md:612]
import torch
from torch import nn

from 학습도구 import 깊은_모델, 데이터_준비, 로더_만들기, 평가, 한_에폭_학습


def 초기화(모델: nn.Module, 방식: str) -> None:
    """모델 안의 모든 선형 층 가중치를 정한 방식으로 다시 채운다."""
    for 층 in 모델.modules():
        if not isinstance(층, nn.Linear):
            continue
        if 방식 == "모두 0":
            nn.init.zeros_(층.weight)
        elif 방식 == "표준편차 0.01":
            nn.init.normal_(층.weight, std=0.01)
        elif 방식 == "Kaiming":
            nn.init.kaiming_normal_(층.weight, nonlinearity="relu")
        nn.init.zeros_(층.bias)


(X_학습, y_학습), (X_검증, y_검증), _ = 데이터_준비(잡음_비율=0.0, 학습_개수=1000)
for 방식 in ["모두 0", "표준편차 0.01", "PyTorch 기본값", "Kaiming"]:
    torch.manual_seed(0)
    로더 = 로더_만들기(X_학습, y_학습)
    모델 = 깊은_모델()
    if 방식 != "PyTorch 기본값":
        초기화(모델, 방식)
    옵티마이저 = torch.optim.SGD(모델.parameters(), lr=0.05)
    for 에폭 in range(20):
        한_에폭_학습(모델, 로더, 옵티마이저)
    손실, 정확도 = 평가(모델, X_검증, y_검증)
    print(f"검증 손실 {손실:.4f}, 정확도 {정확도:5.1%}  <- {방식}")
