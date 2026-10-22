import torch
from torch import nn

torch.manual_seed(0)
모델 = nn.Sequential(
    nn.Linear(4, 8),
    nn.ReLU(),
    nn.Linear(8, 3),
)
print(모델)
print("두 번째 층:", 모델[1], "/ 층 개수:", len(모델))
print(모델(torch.rand(5, 4)).shape)

# 사진을 받는 모델: 맨 앞에서 (1, 28, 28) 사진을 784개 한 줄로 편다
사진_모델 = nn.Sequential(
    nn.Flatten(),                       # (묶음, 1, 28, 28) → (묶음, 784)
    nn.Linear(28 * 28, 64),
    nn.ReLU(),
    nn.Linear(64, 10),
)
사진들 = torch.rand(32, 1, 28, 28)
print(사진_모델[0](사진들).shape, "→", 사진_모델(사진들).shape)
