# [2권 Chapter 14. 언어 모델 다루기: LLM 활용과 LoRA · 14.7 LoRA의 아이디어: 고칠 부분만 작게 · manuscript-vol2/chapters/14-llm-lora.md:774]
import torch
from torch import nn


class LoRA선형층(nn.Module):
    """얼린 nn.Linear 옆에 작은 행렬 두 개(A, B)를 붙인 층."""

    def __init__(self, 원래: nn.Linear, r: int = 4, alpha: int = 8) -> None:
        super().__init__()
        self.원래 = 원래
        self.원래.requires_grad_(False)                  # 원래 가중치는 얼린다 (6장 6.4절)
        self.A = nn.Parameter(torch.randn(r, 원래.in_features) * 0.01)   # 작은 무작위 값
        self.B = nn.Parameter(torch.zeros(원래.out_features, r))       # 0에서 시작
        self.배율 = alpha / r

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.원래(x) + (x @ self.A.T @ self.B.T) * self.배율


torch.manual_seed(0)
원래 = nn.Linear(64, 64)
층 = LoRA선형층(원래, r=4)
x = torch.randn(5, 64)
print("처음에는 원래 층과 출력이 같은가:", torch.allclose(층(x), 원래(x)))
for 이름, p in 층.named_parameters():
    print(f"{이름:14} {tuple(p.shape)!s:10} 학습함={p.requires_grad}")
학습 = sum(p.numel() for p in 층.parameters() if p.requires_grad)
전체 = sum(p.numel() for p in 층.parameters())
print(f"학습하는 숫자 {학습:,}개 / 전체 {전체:,}개")
