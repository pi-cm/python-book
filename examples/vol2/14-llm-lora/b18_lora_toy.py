# [2권 Chapter 14. 언어 모델 다루기: LLM 활용과 LoRA · 14.7 LoRA의 아이디어: 고칠 부분만 작게 · manuscript-vol2/chapters/14-llm-lora.md:827]
import torch
from torch import nn


class LoRA선형층(nn.Module):
    """얼린 nn.Linear 옆에 작은 행렬 두 개(A, B)를 붙인 층 (앞 예제와 같음)."""

    def __init__(self, 원래: nn.Linear, r: int, alpha: int) -> None:
        super().__init__()
        self.원래 = 원래.requires_grad_(False)
        self.A = nn.Parameter(torch.randn(r, 원래.in_features) * 0.01)
        self.B = nn.Parameter(torch.zeros(원래.out_features, r))
        self.배율 = alpha / r

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.원래(x) + (x @ self.A.T @ self.B.T) * self.배율


torch.manual_seed(0)
원래 = nn.Linear(64, 64)
# 목표: 원래 가중치에 "랭크 2짜리 변화"를 더한 층 (예제용으로 만든 정답)
진짜_변화 = torch.randn(64, 2) @ torch.randn(2, 64) * 0.1
x = torch.randn(512, 64)
with torch.no_grad():
    y = x @ (원래.weight + 진짜_변화).T + 원래.bias

for r in [1, 2, 4]:
    torch.manual_seed(1)
    층 = LoRA선형층(원래, r=r, alpha=r)                       # 배율 1로 맞춰 비교
    옵티마이저 = torch.optim.Adam([층.A, 층.B], lr=0.01)
    for 단계 in range(1, 1501):
        손실 = nn.functional.mse_loss(층(x), y)
        옵티마이저.zero_grad()
        손실.backward()
        옵티마이저.step()
    배운_변화 = 층.배율 * 층.B @ 층.A
    오차 = (배운_변화 - 진짜_변화).norm() / 진짜_변화.norm()
    print(f"r={r}: 손실 {손실.item():.6f}, 배운 변화와 진짜 변화의 상대 오차 {오차.item():.3f}")

# 다 배운 뒤에는 W + 배율·(B @ A)를 미리 더해 보통 층 하나로 합칠 수 있다
with torch.no_grad():
    합친 = nn.Linear(64, 64)
    합친.weight.copy_(원래.weight + 층.배율 * 층.B @ 층.A)
    합친.bias.copy_(원래.bias)
    print("합친 층과 LoRA 층의 출력이 같은가:", torch.allclose(합친(x), 층(x), atol=1e-5))
