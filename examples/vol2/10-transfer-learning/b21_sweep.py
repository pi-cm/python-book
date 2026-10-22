# [2권 Chapter 10. 전이 학습: 남이 학습한 모델 빌려 쓰기 · 10.9 실습: 데이터가 적을수록 전이 학습이 빛난다 · manuscript-vol2/chapters/10-transfer-learning.md:1166]
import itertools

import torch
from torch import nn
from torchvision import models

from 전이도구 import 로더_만들기, 유로샛_불러오기, 장치_고르기, 머리_학습, 정확도, 특징_뽑기

장치 = 장치_고르기()
검증_사진, 검증_정답 = 유로샛_불러오기("검증", 100)
검증_로더 = 로더_만들기(검증_사진, 검증_정답)


def 끝없이(로더):
    """로더를 다 돌면 처음부터 다시 돈다. 돌 때마다 새로 섞고 새로 증강한다."""
    while True:
        yield from 로더


def 고치기(모델: nn.Module, 옵티마이저: torch.optim.Optimizer, 학습_로더, 횟수: int) -> None:
    """데이터 양과 상관없이 정해진 횟수만큼 배치를 꺼내 고친다."""
    모델.train()
    for x, y in itertools.islice(끝없이(학습_로더), 횟수):
        x, y = x.to(장치), y.to(장치)
        옵티마이저.zero_grad()
        nn.functional.cross_entropy(모델(x), y).backward()
        옵티마이저.step()


def 처음부터(학습_로더) -> float:
    torch.manual_seed(0)
    모델 = models.resnet18(weights=None, num_classes=10).to(장치)
    고치기(모델, torch.optim.Adam(모델.parameters(), lr=1e-3), 학습_로더, 240)
    return 정확도(모델, 검증_로더, 장치)


def 특징_추출(학습_사진, 학습_정답) -> float:
    몸통 = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    몸통.fc = nn.Identity()
    몸통.to(장치)
    학습_특징, _ = 특징_뽑기(몸통, 로더_만들기(학습_사진, 학습_정답), 장치)
    검증_특징, _ = 특징_뽑기(몸통, 검증_로더, 장치)
    머리 = 머리_학습(학습_특징, 학습_정답)
    with torch.no_grad():
        return (머리(검증_특징).argmax(1) == 검증_정답).float().mean().item()


def 미세조정(학습_로더) -> float:
    torch.manual_seed(0)
    모델 = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    모델.fc = nn.Linear(512, 10)
    모델.to(장치)
    몸통_파라미터 = [p for 이름, p in 모델.named_parameters() if not 이름.startswith("fc.")]
    옵티마이저 = torch.optim.Adam([{"params": 몸통_파라미터, "lr": 1e-4},
                                {"params": 모델.fc.parameters(), "lr": 1e-3}])
    고치기(모델, 옵티마이저, 학습_로더, 64)
    return 정확도(모델, 검증_로더, 장치)


print("클래스당 | 처음부터 | 특징 추출 | 미세조정")
for 클래스당 in [5, 20, 100]:
    학습_사진, 학습_정답 = 유로샛_불러오기("학습", 클래스당)
    학습_로더 = 로더_만들기(학습_사진, 학습_정답, 증강=True, 섞기=True)
    결과 = [처음부터(학습_로더), 특징_추출(학습_사진, 학습_정답), 미세조정(학습_로더)]
    print(f"{클래스당:6}장 | " + " | ".join(f"{a:7.1%}" for a in 결과))
