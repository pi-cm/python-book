# [2권 Chapter 11. RNN과 LSTM: 순서가 있는 데이터 · 11.10 시계열 예측: 마우나로아 이산화탄소 · manuscript-vol2/chapters/11-rnn-lstm.md:1065]
import torch
from statsmodels.datasets import co2

월간 = co2.load_pandas().data["co2"].resample("MS").mean().interpolate()
값 = torch.tensor(월간.values, dtype=torch.float32)

창 = 24                                           # 지난 24개월을 보고 다음 달을 맞힌다
X = 값.unfold(0, 창, 1)[:-1]                      # (502, 24)
y = 값[창:]                                       # (502,)
날짜 = 월간.index[창:]                            # 정답 달의 날짜

# 시간 순서로 자르기(2장 2.9절): 1990년까지 학습, 1991~1995년 검증, 1996년부터 테스트
학습 = torch.tensor(날짜 < "1991-01-01")
검증 = torch.tensor((날짜 >= "1991-01-01") & (날짜 < "1996-01-01"))
테스트 = torch.tensor(날짜 >= "1996-01-01")
print("학습", 학습.sum().item(), "검증", 검증.sum().item(), "테스트", 테스트.sum().item())


def rmse(예측: torch.Tensor, 정답: torch.Tensor) -> float:
    return ((예측 - 정답) ** 2).mean().sqrt().item()


지난달 = X[:, -1]                                  # 기준선 1: 지난달 값 그대로
작년_같은달 = X[:, -12] + (X[:, -1] - X[:, -13])   # 기준선 2: 작년 같은 달 + 1년 동안 오른 만큼
for 이름, 예측 in [("지난달 그대로", 지난달), ("작년 같은 달 + 1년 증가분", 작년_같은달)]:
    print(f"{이름}: 검증 RMSE {rmse(예측[검증], y[검증]):.3f}, 테스트 RMSE {rmse(예측[테스트], y[테스트]):.3f} ppm")
