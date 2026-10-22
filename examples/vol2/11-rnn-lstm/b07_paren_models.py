# [2권 Chapter 11. RNN과 LSTM: 순서가 있는 데이터 · 11.3 순서를 알아야 풀리는 문제: 괄호 짝 맞추기 · manuscript-vol2/chapters/11-rnn-lstm.md:364]
import torch
from torch import nn

from 괄호도구 import 괄호_만들기, 원핫으로

괄호_학습, y_학습 = 괄호_만들기(3000, [20], 씨앗=0)      # 길이 20짜리 괄호만
괄호_검증, y_검증 = 괄호_만들기(1000, [20], 씨앗=1)
X_학습, _ = 원핫으로(괄호_학습)                          # (3000, 20, 3)
X_검증, _ = 원핫으로(괄호_검증)


class 개수_모델(nn.Module):
    """글자 개수만 보는 모델: 순서를 버린다."""
    def __init__(self) -> None:
        super().__init__()
        self.mlp = nn.Sequential(nn.Linear(3, 32), nn.ReLU(), nn.Linear(32, 2))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.mlp(x.sum(dim=1))              # (배치, 20, 3) → (배치, 3)


class 순환_모델(nn.Module):
    """한 글자씩 읽으며 메모를 고쳐 쓰고, 마지막 메모로 판단한다."""
    def __init__(self, 메모_크기: int = 32) -> None:
        super().__init__()
        self.rnn = nn.RNN(3, 메모_크기, batch_first=True)
        self.판단 = nn.Linear(메모_크기, 2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        _, h_n = self.rnn(x)
        return self.판단(h_n[-1])                  # 마지막 층의 마지막 메모


def 학습_평가(모델: nn.Module, 에폭_수: int = 30) -> tuple[float, float]:
    torch.manual_seed(0)
    옵티마이저 = torch.optim.Adam(모델.parameters(), lr=3e-3)
    for _ in range(에폭_수):
        for 묶음 in torch.randperm(len(X_학습)).split(64):
            손실 = nn.functional.cross_entropy(모델(X_학습[묶음]), y_학습[묶음])
            옵티마이저.zero_grad()
            손실.backward()
            옵티마이저.step()
    with torch.no_grad():
        정확도 = lambda X, y: (모델(X).argmax(dim=1) == y).float().mean().item()
        return 정확도(X_학습, y_학습), 정확도(X_검증, y_검증)


torch.manual_seed(0)
모델들 = {"개수만 보는 MLP": 개수_모델(),
          "펼쳐서 보는 MLP": nn.Sequential(nn.Flatten(), nn.Linear(20 * 3, 64), nn.ReLU(), nn.Linear(64, 2)),
          "RNN": 순환_모델()}
for 이름, 모델 in 모델들.items():
    학습, 검증 = 학습_평가(모델)
    개수 = sum(p.numel() for p in 모델.parameters())
    print(f"{이름}: 파라미터 {개수:,}개, 학습 {학습:.1%}, 검증 {검증:.1%}")
