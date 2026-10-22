import torch
from torch import nn

torch.manual_seed(0)
드롭아웃 = nn.Dropout(p=0.5)                 # 칸마다 50% 확률로 끈다
x = torch.ones(10)

드롭아웃.train()                              # 학습 모드
print("학습 모드 1번째:", 드롭아웃(x))
print("학습 모드 2번째:", 드롭아웃(x))

드롭아웃.eval()                               # 평가 모드
print("평가 모드 1번째:", 드롭아웃(x))
print("평가 모드 2번째:", 드롭아웃(x))

큰_x = torch.ones(100_000)
드롭아웃.train()
print(f"학습 모드 평균: {드롭아웃(큰_x).mean().item():.4f}")
