# [2권 Chapter 12. 어텐션과 트랜스포머: 처음부터 직접 구현 · 12.7 트랜스포머 블록 조립하기 · manuscript-vol2/chapters/12-transformer.md:713]
import torch
from torch import nn

torch.manual_seed(0)
깊이 = 32
층들 = nn.ModuleList(nn.Sequential(nn.Linear(64, 64), nn.Tanh()) for _ in range(깊이))
x = torch.randn(16, 64)

for 잔차 in (False, True):
    층들.zero_grad()
    h = x
    for 층 in 층들:
        h = h + 층(h) if 잔차 else 층(h)        # 잔차 연결: 입력을 출력에 더해 준다
    h.pow(2).mean().backward()
    첫층 = 층들[0][0].weight.grad.norm().item()
    끝층 = 층들[-1][0].weight.grad.norm().item()
    print(f"잔차 {'있음' if 잔차 else '없음'}: 첫 층 기울기 {첫층:.2e}, 마지막 층 기울기 {끝층:.2e}")
