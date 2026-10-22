# [2권 Chapter 10. 전이 학습: 남이 학습한 모델 빌려 쓰기 · 10.6 미세조정: 몸통까지 조금씩 고치기 · manuscript-vol2/chapters/10-transfer-learning.md:860]
import torch
from torch import nn
from torchvision import models

from 전이도구 import 로더_만들기, 유로샛_불러오기, 장치_고르기, 정확도

장치 = 장치_고르기()
학습_사진, 학습_정답 = 유로샛_불러오기("학습", 50)
검증_사진, 검증_정답 = 유로샛_불러오기("검증", 100)
학습_로더 = 로더_만들기(학습_사진, 학습_정답, 증강=True, 섞기=True)
검증_로더 = 로더_만들기(검증_사진, 검증_정답)

순서 = ["conv1", "bn1", "layer1", "layer2", "layer3", "layer4"]   # 입력에 가까운 쪽부터
for 풀_개수 in [0, 1, 2, 4, 6]:                                    # 뒤에서부터 몇 부분을 풀까
    얼린_부분, 풀_부분 = 순서[:len(순서) - 풀_개수], 순서[len(순서) - 풀_개수:]
    torch.manual_seed(0)
    모델 = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    for 이름 in 얼린_부분:
        모델.get_submodule(이름).requires_grad_(False)
    모델.fc = nn.Linear(512, 10)
    모델.to(장치)
    몸통_파라미터 = [p for 이름, p in 모델.named_parameters() if p.requires_grad and not 이름.startswith("fc.")]
    옵티마이저 = torch.optim.Adam([{"params": 몸통_파라미터, "lr": 1e-4},
                                {"params": 모델.fc.parameters(), "lr": 1e-3}])
    for 에폭 in range(8):
        모델.train()
        for 이름 in 얼린_부분:                  # 얼린 부분은 배치 정규화 기록도 그대로 둔다(10.4절)
            모델.get_submodule(이름).eval()
        for x, y in 학습_로더:
            x, y = x.to(장치), y.to(장치)
            옵티마이저.zero_grad()
            nn.functional.cross_entropy(모델(x), y).backward()
            옵티마이저.step()
    학습_대상 = sum(p.numel() for p in 모델.parameters() if p.requires_grad)
    print(f"학습 대상 {학습_대상:>10,}개, 검증 {정확도(모델, 검증_로더, 장치):.1%} ← 푼 부분: {', '.join(풀_부분) or '없음(머리만)'}")
