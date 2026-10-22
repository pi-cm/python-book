# [2권 Chapter 10. 전이 학습: 남이 학습한 모델 빌려 쓰기 · 10.6 미세조정: 몸통까지 조금씩 고치기 · manuscript-vol2/chapters/10-transfer-learning.md:800]
import torch
from torch import nn
from torchvision import models

from 전이도구 import 로더_만들기, 유로샛_불러오기, 장치_고르기, 정확도, 한_에폭_학습

모델 = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
모델.fc = nn.Linear(512, 10)

# 몸통과 머리를 나눠 학습률을 따로 준다
몸통_파라미터 = [p for 이름, p in 모델.named_parameters() if not 이름.startswith("fc.")]
옵티마이저 = torch.optim.Adam([
    {"params": 몸통_파라미터, "lr": 1e-4},          # 이미 잘 배운 부분은 조심스럽게
    {"params": 모델.fc.parameters(), "lr": 1e-3},   # 처음 배우는 머리는 크게
])
for i, 그룹 in enumerate(옵티마이저.param_groups):
    개수 = sum(p.numel() for p in 그룹["params"])
    print(f"그룹 {i}: 텐서 {len(그룹['params'])}개, 파라미터 {개수:,}개, lr={그룹['lr']:g}")

# 같은 조건에서 "전부 1e-4"와 비교한다
장치 = 장치_고르기()
학습_사진, 학습_정답 = 유로샛_불러오기("학습", 50)
검증_사진, 검증_정답 = 유로샛_불러오기("검증", 100)
학습_로더 = 로더_만들기(학습_사진, 학습_정답, 증강=True, 섞기=True)
검증_로더 = 로더_만들기(검증_사진, 검증_정답)

for 방법 in ["전부 1e-4", "몸통 1e-4 + 머리 1e-3"]:
    torch.manual_seed(0)
    모델 = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    모델.fc = nn.Linear(512, 10)
    모델.to(장치)
    if 방법 == "전부 1e-4":
        옵티마이저 = torch.optim.Adam(모델.parameters(), lr=1e-4)
    else:
        몸통_파라미터 = [p for 이름, p in 모델.named_parameters() if not 이름.startswith("fc.")]
        옵티마이저 = torch.optim.Adam([{"params": 몸통_파라미터, "lr": 1e-4},
                                    {"params": 모델.fc.parameters(), "lr": 1e-3}])
    기록 = []
    for 에폭 in range(8):
        한_에폭_학습(모델, 학습_로더, 옵티마이저, 장치)
        기록.append(정확도(모델, 검증_로더, 장치))
    print(f"{방법}: 에폭별 검증 정확도", " ".join(f"{a:.1%}" for a in 기록))
