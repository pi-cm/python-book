# [2권 Chapter 10. 전이 학습: 남이 학습한 모델 빌려 쓰기 · 10.2 입력 전처리 맞추기 · manuscript-vol2/chapters/10-transfer-learning.md:156]
import torch
from torchvision import datasets, models
from torchvision.transforms import v2

전처리 = models.ResNet18_Weights.DEFAULT.transforms()
print(전처리)

사진, 정답 = datasets.EuroSAT("data", download=True)[0]
print("원본:", 사진.size, 사진.mode)
x = 전처리(사진)
print("전처리 후:", tuple(x.shape), x.dtype)

# 같은 일을 7장의 v2 변환으로 풀어 쓰면
풀어쓰기 = v2.Compose([
    v2.ToImage(),
    v2.Resize(256),                 # 짧은 변을 256으로
    v2.CenterCrop(224),             # 가운데 224 × 224
    v2.ToDtype(torch.float32, scale=True),
    v2.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])
print("풀어 쓴 것과 같은가:", torch.allclose(풀어쓰기(사진), x, atol=1e-5))
