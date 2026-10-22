# [2권 Chapter 6. nn.Module과 학습 루프: 모든 모델이 따르는 표준형 · 6.10 모델 저장과 불러오기 · manuscript-vol2/chapters/06-nn-module.md:1046]
import torch
from torch import nn

torch.manual_seed(0)
모델 = nn.Linear(3, 1)
옵티마이저 = torch.optim.Adam(모델.parameters(), lr=0.01)
x, y = torch.rand(16, 3), torch.rand(16, 1)
for _ in range(5):                              # 5에폭 학습했다고 하자
    옵티마이저.zero_grad()
    nn.functional.mse_loss(모델(x), y).backward()
    옵티마이저.step()

# 이어서 학습할 수 있게 필요한 것을 한 상자에
torch.save({
    "에폭": 5,
    "모델": 모델.state_dict(),
    "옵티마이저": 옵티마이저.state_dict(),
}, "체크포인트.pt")

# 다음 날: 같은 설계도로 만들고 상자를 열어 채운다
새_모델 = nn.Linear(3, 1)
새_옵티마이저 = torch.optim.Adam(새_모델.parameters(), lr=0.01)
상자 = torch.load("체크포인트.pt", weights_only=True)
새_모델.load_state_dict(상자["모델"])
새_옵티마이저.load_state_dict(상자["옵티마이저"])
print("이어서 시작할 에폭:", 상자["에폭"] + 1)
print("옵티마이저가 기억하는 것:", list(상자["옵티마이저"]["state"][0].keys()))
