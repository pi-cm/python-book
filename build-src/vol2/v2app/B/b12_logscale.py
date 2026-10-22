import numpy as np

# 0.0001에서 0.1 사이에서 후보 7개 고르기
print("고르게  :", np.round(np.linspace(1e-4, 1e-1, 7), 4))
print("로그 눈금:", np.round(np.logspace(-4, -1, 7), 5))
print("log10   :", np.round(np.log10(np.logspace(-4, -1, 7)), 2))
