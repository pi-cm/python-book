# [2권 Chapter 11. RNN과 LSTM: 순서가 있는 데이터 · 11.9 길이가 다른 순서열: pack_padded_sequence · manuscript-vol2/chapters/11-rnn-lstm.md:950]
import torch
from torch import nn
from torch.nn.utils.rnn import pack_padded_sequence

from 괄호도구 import 괄호_만들기, 원핫으로

학습_길이들 = list(range(2, 21, 2))                  # 2, 4, ..., 20 글자를 섞어서
괄호_학습, y_학습 = 괄호_만들기(6000, 학습_길이들, 씨앗=0)
X_학습, 길이_학습 = 원핫으로(괄호_학습)
print("학습 배치 모양:", tuple(X_학습.shape), "가장 짧은/긴 길이:", 길이_학습.min().item(), 길이_학습.max().item())


class 괄호_판정기(nn.Module):
    def __init__(self, 종류: type[nn.Module], 꾸릴까: bool) -> None:
        super().__init__()
        self.꾸릴까 = 꾸릴까
        self.순환 = 종류(3, 32, batch_first=True)
        self.판단 = nn.Linear(32, 2)

    def forward(self, x: torch.Tensor, 길이: torch.Tensor) -> torch.Tensor:
        if self.꾸릴까:
            x = pack_padded_sequence(x, 길이, batch_first=True, enforce_sorted=False)
        _, 상태 = self.순환(x)
        h_n = 상태[0] if isinstance(상태, tuple) else 상태   # LSTM은 (h_n, c_n)
        return self.판단(h_n[-1])


def 정확도(모델: nn.Module, 길이들: list[int], 씨앗: int) -> float:
    괄호들, 정답 = 괄호_만들기(1000, 길이들, 씨앗)
    X, 길이 = 원핫으로(괄호들)
    with torch.no_grad():
        return (모델(X, 길이).argmax(dim=1) == 정답).float().mean().item()


print("모델         꾸러미   검증(2~20)  길이 30  길이 40  길이 60")
for 종류 in [nn.RNN, nn.LSTM]:
    for 꾸릴까 in [False, True]:
        torch.manual_seed(0)
        모델 = 괄호_판정기(종류, 꾸릴까)
        옵티마이저 = torch.optim.Adam(모델.parameters(), lr=3e-3)
        for _ in range(15):
            for 묶음 in torch.randperm(len(X_학습)).split(64):
                손실 = nn.functional.cross_entropy(모델(X_학습[묶음], 길이_학습[묶음]), y_학습[묶음])
                옵티마이저.zero_grad()
                손실.backward()
                옵티마이저.step()
        결과 = [정확도(모델, 학습_길이들, 1)] + [정확도(모델, [n], 2) for n in (30, 40, 60)]
        print(f"{종류.__name__:5}  {'씀' if 꾸릴까 else '안 씀':4}  " + "  ".join(f"{r:8.1%}" for r in 결과))
