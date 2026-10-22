# [2권 Chapter 10. 전이 학습: 남이 학습한 모델 빌려 쓰기 · 10.4 특징 추출: 눈은 빌리고 판단만 새로 · manuscript-vol2/chapters/10-transfer-learning.md:596]
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from torchvision import models
from torchvision.transforms import v2

from 전이도구 import 유로샛_불러오기, 장치_고르기, 머리_학습, 특징_뽑기

장치 = 장치_고르기()
몸통 = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
몸통.fc = nn.Identity()
몸통.to(장치)
학습_사진, 학습_정답 = 유로샛_불러오기("학습", 50)
검증_사진, 검증_정답 = 유로샛_불러오기("검증", 100)

# 우리 데이터(학습 사진)에서 직접 구한 채널별 평균·표준편차
실수 = 학습_사진.float() / 255
우리_평균, 우리_표준편차 = 실수.mean(dim=(0, 2, 3)).tolist(), 실수.std(dim=(0, 2, 3)).tolist()
print("우리 데이터 평균:", [f"{v:.3f}" for v in 우리_평균], "표준편차:", [f"{v:.3f}" for v in 우리_표준편차])

크기_맞추기 = [v2.Resize(112), v2.ToDtype(torch.float32, scale=True)]
방법들 = {
    "ImageNet 기준 정규화": v2.Compose(크기_맞추기 + [v2.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])]),
    "우리 데이터 기준 정규화": v2.Compose(크기_맞추기 + [v2.Normalize(우리_평균, 우리_표준편차)]),
    "정규화 빼먹기(0~1)": v2.Compose(크기_맞추기),
    "scale 빼먹기(0~255)": v2.Compose([v2.Resize(112), v2.ToDtype(torch.float32),
                                     v2.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])]),
}


def 로더(사진: torch.Tensor, 정답: torch.Tensor, 변환: v2.Compose) -> DataLoader:
    return DataLoader(TensorDataset(변환(사진), 정답), batch_size=64)   # 묶음 전체를 한 번에 변환


for 이름, 변환 in 방법들.items():
    학습_특징, _ = 특징_뽑기(몸통, 로더(학습_사진, 학습_정답, 변환), 장치)
    검증_특징, _ = 특징_뽑기(몸통, 로더(검증_사진, 검증_정답, 변환), 장치)
    머리 = 머리_학습(학습_특징, 학습_정답)
    with torch.no_grad():
        정확도 = (머리(검증_특징).argmax(1) == 검증_정답).float().mean()
    print(f"검증 정확도 {정확도:6.1%}  {이름}")
