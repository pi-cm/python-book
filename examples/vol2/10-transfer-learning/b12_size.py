# [2권 Chapter 10. 전이 학습: 남이 학습한 모델 빌려 쓰기 · 10.4 특징 추출: 눈은 빌리고 판단만 새로 · manuscript-vol2/chapters/10-transfer-learning.md:661]
import torch
from torch import nn
from torch.utils.flop_counter import FlopCounterMode
from torchvision import models

from 전이도구 import 로더_만들기, 유로샛_불러오기, 장치_고르기, 머리_학습, 특징_뽑기

장치 = 장치_고르기()
몸통 = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
몸통.fc = nn.Identity()
몸통.eval()                                  # 세는 동안에도 배치 정규화 기록이 바뀌지 않게
학습_사진, 학습_정답 = 유로샛_불러오기("학습", 50)
검증_사진, 검증_정답 = 유로샛_불러오기("검증", 100)

for 크기 in [64, 112, 160, 224]:
    with FlopCounterMode(display=False) as 계수기:      # 사진 한 장에 드는 곱셈·덧셈 수 세기
        몸통.cpu()(torch.zeros(1, 3, 크기, 크기))
    몸통.to(장치)
    학습_특징, _ = 특징_뽑기(몸통, 로더_만들기(학습_사진, 학습_정답, 크기=크기), 장치)
    검증_특징, _ = 특징_뽑기(몸통, 로더_만들기(검증_사진, 검증_정답, 크기=크기), 장치)
    머리 = 머리_학습(학습_특징, 학습_정답)
    with torch.no_grad():
        정확도 = (머리(검증_특징).argmax(1) == 검증_정답).float().mean()
    print(f"{크기:3} × {크기:3}: 한 장에 {계수기.get_total_flops() / 1e9:5.2f} GFLOP, 검증 정확도 {정확도:.1%}")
