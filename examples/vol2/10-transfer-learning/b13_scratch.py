# [2권 Chapter 10. 전이 학습: 남이 학습한 모델 빌려 쓰기 · 10.5 처음부터 학습하면 어떨까 · manuscript-vol2/chapters/10-transfer-learning.md:703]
import torch
from torchvision import models

from 전이도구 import 로더_만들기, 유로샛_불러오기, 장치_고르기, 정확도, 한_에폭_학습

장치 = 장치_고르기()
학습_사진, 학습_정답 = 유로샛_불러오기("학습", 50)
검증_사진, 검증_정답 = 유로샛_불러오기("검증", 100)
학습_로더 = 로더_만들기(학습_사진, 학습_정답, 증강=True, 섞기=True)
학습_평가_로더 = 로더_만들기(학습_사진, 학습_정답)          # 증강 없이 학습 정확도를 잴 때
검증_로더 = 로더_만들기(검증_사진, 검증_정답)

torch.manual_seed(0)
모델 = models.resnet18(weights=None, num_classes=10).to(장치)   # 같은 구조, 무작위 가중치
옵티마이저 = torch.optim.Adam(모델.parameters(), lr=1e-3)
for 에폭 in range(1, 31):
    손실 = 한_에폭_학습(모델, 학습_로더, 옵티마이저, 장치)
    if 에폭 % 5 == 0:
        print(f"에폭 {에폭:2}: 손실 {손실:.3f}, 학습 {정확도(모델, 학습_평가_로더, 장치):.1%}, "
              f"검증 {정확도(모델, 검증_로더, 장치):.1%}")
