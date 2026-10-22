import statsmodels, pandas
from statsmodels.datasets import co2
d = co2.load_pandas().data
print(statsmodels.__version__, pandas.__version__)
print(d.shape, d.index[:3], d.index[-3:], d.isna().sum())
m = d["co2"].resample("MS").mean()
print(m.shape, m.isna().sum(), m.head(), m.tail())
print(co2.COPYRIGHT, co2.SOURCE[:300])
