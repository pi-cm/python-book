# [2권 Chapter 11. RNN과 LSTM: 순서가 있는 데이터 · 11.10 시계열 예측: 마우나로아 이산화탄소 · manuscript-vol2/chapters/11-rnn-lstm.md:1111]
import copy

import torch
from statsmodels.datasets import co2
from torch import nn

월간 = co2.load_pandas().data["co2"].resample("MS").mean().interpolate()
값 = torch.tensor(월간.values, dtype=torch.float32)
창 = 24
X, y, 날짜 = 값.unfold(0, 창, 1)[:-1], 값[창:], 월간.index[창:]
학습 = torch.tensor(날짜 < "1991-01-01")
검증 = torch.tensor((날짜 >= "1991-01-01") & (날짜 < "1996-01-01"))
테스트 = torch.tensor(날짜 >= "1996-01-01")

# 절대값 대신 '마지막 달과의 차이'를 보고 '다음 달에 얼마나 변할지'를 맞힌다
마지막 = X[:, -1:]
입력, 목표 = X - 마지막, y - 마지막[:, 0]
척도 = 입력[학습].std()                            # 학습 구간에서만 잰 크기로 나눈다
입력, 목표 = 입력 / 척도, 목표 / 척도


class 예측기(nn.Module):
    def __init__(self, 종류: type[nn.Module]) -> None:
        super().__init__()
        self.순환 = 종류(1, 32, batch_first=True)
        self.답 = nn.Linear(32, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        출력, _ = self.순환(x.unsqueeze(-1))       # (배치, 24) → (배치, 24, 1)
        return self.답(출력[:, -1]).squeeze(-1)


def ppm_rmse(모델: nn.Module, 구간: torch.Tensor) -> float:
    with torch.no_grad():
        예측 = 모델(입력[구간]) * 척도 + 마지막[구간, 0]   # 차이를 다시 ppm 값으로
    return ((예측 - y[구간]) ** 2).mean().sqrt().item()


가장_좋은 = (float("inf"), None)
for 종류 in [nn.RNN, nn.LSTM, nn.GRU]:
    torch.manual_seed(0)
    모델 = 예측기(종류)
    옵티마이저 = torch.optim.Adam(모델.parameters(), lr=3e-3)
    X_학습, y_학습 = 입력[학습], 목표[학습]
    최고 = (float("inf"), 0, None)
    for 에폭 in range(1, 201):
        for 묶음 in torch.randperm(len(X_학습)).split(32):
            손실 = nn.functional.mse_loss(모델(X_학습[묶음]), y_학습[묶음])
            옵티마이저.zero_grad()
            손실.backward()
            옵티마이저.step()
        검증_오차 = ppm_rmse(모델, 검증)
        if 검증_오차 < 최고[0]:                    # 검증 오차가 가장 낮았던 순간을 보관(8.8절)
            최고 = (검증_오차, 에폭, copy.deepcopy(모델.state_dict()))
    모델.load_state_dict(최고[2])
    print(f"{종류.__name__:4}: {최고[1]:3d}에폭 선택, 검증 RMSE {최고[0]:.3f}, 테스트 RMSE {ppm_rmse(모델, 테스트):.3f} ppm")
    if 최고[0] < 가장_좋은[0]:                     # 검증 성적으로 하나를 골라 저장
        가장_좋은 = (최고[0], 종류.__name__)
        torch.save({"종류": 종류.__name__, "가중치": 최고[2], "척도": 척도}, "co2_모델.pt")
print("저장한 모델:", 가장_좋은[1])
