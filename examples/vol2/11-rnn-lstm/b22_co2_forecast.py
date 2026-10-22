# [2권 Chapter 11. RNN과 LSTM: 순서가 있는 데이터 · 11.10 시계열 예측: 마우나로아 이산화탄소 · manuscript-vol2/chapters/11-rnn-lstm.md:1189]
import matplotlib.pyplot as plt
import torch
from statsmodels.datasets import co2
from torch import nn

월간 = co2.load_pandas().data["co2"].resample("MS").mean().interpolate()
값 = torch.tensor(월간.values, dtype=torch.float32)
시작 = 월간.index.get_loc(월간["1996-01"].index[0])  # 테스트 첫 달의 위치
개월 = len(값) - 시작                                # 1996년 1월부터 2001년 12월까지 72개월


class 예측기(nn.Module):                            # 앞 예제와 같은 구조
    def __init__(self, 종류: type[nn.Module]) -> None:
        super().__init__()
        self.순환 = 종류(1, 32, batch_first=True)
        self.답 = nn.Linear(32, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        출력, _ = self.순환(x.unsqueeze(-1))
        return self.답(출력[:, -1]).squeeze(-1)


저장본 = torch.load("co2_모델.pt", weights_only=True)   # 앞 예제에서 검증 성적으로 고른 모델
모델 = 예측기(getattr(nn, 저장본["종류"]))
모델.load_state_dict(저장본["가중치"])
척도 = 저장본["척도"]

# 1995년 12월까지만 알고, 그 뒤 72개월을 자기 예측을 이어 붙이며 내다본다
모델_예측 = 값[:시작].clone()
기준선 = 값[:시작].clone()
with torch.no_grad():
    for _ in range(개월):
        창 = 모델_예측[-24:]
        변화 = 모델((창 - 창[-1]).unsqueeze(0) / 척도) * 척도
        모델_예측 = torch.cat([모델_예측, 창[-1:] + 변화])
        다음 = 기준선[-12] + (기준선[-1] - 기준선[-13])   # 작년 같은 달 + 1년 증가분
        기준선 = torch.cat([기준선, 다음.unsqueeze(0)])

실제 = 값[시작:]
for 이름, 예측 in [(저장본["종류"] + " 이어 예측", 모델_예측[시작:]), ("기준선 이어 예측", 기준선[시작:])]:
    오차 = 예측 - 실제
    print(f"{이름}: 첫 12개월 RMSE {오차[:12].pow(2).mean().sqrt():.3f}, "
          f"72개월 RMSE {오차.pow(2).mean().sqrt():.3f}, 2001년 12월 오차 {오차[-1]:+.2f} ppm")

연평균 = 월간.groupby(월간.index.year).mean()
print(f"연간 증가량: 1959~1990년 평균 {(연평균[1990] - 연평균[1959]) / 31:.2f}ppm, "
      f"1995~2001년 평균 {(연평균[2001] - 연평균[1995]) / 6:.2f}ppm")

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False
plt.figure(figsize=(7, 3.5))
보기 = slice(시작 - 48, None)                        # 1992년부터 그린다
plt.plot(월간.index[보기], 값[보기], color="black", label="실제 측정값")
plt.plot(월간.index[시작:], 모델_예측[시작:], label=f"{저장본['종류']} 이어 예측")
plt.plot(월간.index[시작:], 기준선[시작:], linestyle="--", label="기준선 이어 예측")
plt.axvline(월간.index[시작], color="gray", linestyle=":")
plt.ylabel("CO2 (ppm)")
plt.legend()
plt.tight_layout()
plt.savefig("co2_forecast.png", dpi=200)
