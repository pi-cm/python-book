# [2권 Chapter 6. nn.Module과 학습 루프: 모든 모델이 따르는 표준형 · 6.1 층 하나: 입력 @ 가중치 + 편향 · manuscript-vol2/chapters/06-nn-module.md:34]
import torch

# 손님 4명 × 특성 3개(방문 횟수, 머문 시간, 장바구니 금액). 예제용 숫자입니다.
x = torch.tensor([[0.2, 0.5, 0.1],
                  [0.9, 0.1, 0.4],
                  [0.4, 0.8, 0.7],
                  [0.6, 0.3, 0.2]])

torch.manual_seed(0)
가중치 = torch.randn(3, 2)          # 입력 3개 → 출력 2개
편향 = torch.zeros(2)               # 출력마다 하나씩

출력 = x @ 가중치 + 편향              # (4, 3) @ (3, 2) + (2,) → (4, 2)
print(가중치)
print(출력)
print("모양:", 출력.shape)

# 첫 손님의 첫 번째 출력을 풀어 쓰면
print((x[0] * 가중치[:, 0]).sum() + 편향[0])
