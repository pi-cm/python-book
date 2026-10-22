# [2권 Chapter 17. 분산·대규모 학습: 메모리를 아끼고 GPU를 늘리기 · 17.1 학습 중 GPU 메모리는 어디에 쓰일까 · manuscript-vol2/chapters/17-distributed-training.md:40]
import torch
from torch import nn

assert torch.cuda.is_available(), "이 예제는 NVIDIA GPU가 있어야 합니다"
장치 = torch.device("cuda")
MB = 1024 ** 2


def 찍기(시점: str) -> None:
    """지금 텐서들이 차지한 GPU 메모리를 MB로 보여 준다."""
    print(f"{시점:>16}: {torch.cuda.memory_allocated() / MB:6,.0f} MB")


torch.manual_seed(0)
# 4096 → 4096 선형층 8개: 파라미터 약 1억 3천만 개
모델 = nn.Sequential(*[nn.Sequential(nn.Linear(4096, 4096), nn.ReLU()) for _ in range(8)]).to(장치)
개수 = sum(p.numel() for p in 모델.parameters())
print(f"파라미터 {개수:,}개 × 4바이트 = {개수 * 4 / MB:,.0f} MB")

옵티마이저 = torch.optim.Adam(모델.parameters(), lr=1e-4)
x = torch.randn(2048, 4096, device=장치)          # 입력 2048개 묶음 (32MB)
찍기("모델·입력 올린 뒤")
for 번째 in (1, 2):
    torch.cuda.reset_peak_memory_stats()
    손실 = 모델(x).pow(2).mean()
    찍기(f"{번째}회 forward 뒤")       # 활성화가 쌓였다
    손실.backward()
    찍기(f"{번째}회 backward 뒤")      # 활성화는 풀리고 기울기가 생겼다
    옵티마이저.step()
    찍기(f"{번째}회 step 뒤")          # 첫 step에서 Adam 상태가 생긴다
    옵티마이저.zero_grad()
    찍기(f"{번째}회 zero_grad 뒤")     # 기울기를 None으로 비운다
    print(f"{f'{번째}회 중 최고':>16}: {torch.cuda.max_memory_allocated() / MB:6,.0f} MB")

상태 = 옵티마이저.state[모델[0][0].weight]
print("Adam이 가중치마다 기억하는 것:", [k for k, v in 상태.items() if v.numel() > 1])
