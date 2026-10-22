# [2권 Chapter 11. RNN과 LSTM: 순서가 있는 데이터 · 11.10 시계열 예측: 마우나로아 이산화탄소 · manuscript-vol2/chapters/11-rnn-lstm.md:1033]
from statsmodels.datasets import co2

주간 = co2.load_pandas().data["co2"]                # 1958~2001년 주간 측정값 (ppm)
print(주간.shape, "빈 값:", 주간.isna().sum())

월간 = 주간.resample("MS").mean()                  # 달마다 평균 (MS: 매달 1일 기준)
print("달 수:", len(월간), "빈 달:", 월간.isna().sum())
월간 = 월간.interpolate()                          # 빈 달은 앞뒤 달 사이 값으로 메운다
print(월간.index[0].date(), "~", 월간.index[-1].date())

연평균 = 월간.groupby(월간.index.year).mean()
print("연평균:", 연평균[[1960, 1970, 1980, 1990, 2000]].round(1).to_dict())
print("2000년 달마다:", 월간["2000"].round(1).tolist())
