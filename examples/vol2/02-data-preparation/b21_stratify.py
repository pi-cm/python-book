# [2권 Chapter 2. 데이터 준비: 모델에 넣기 전에 할 일 · 2.8 불균형 데이터 · manuscript-vol2/chapters/02-data-preparation.md:885]
import numpy as np
from sklearn.model_selection import train_test_split

y = np.array([1] * 10 + [0] * 90)      # 100명 중 10명만 양성 (10%)
X = np.arange(100).reshape(-1, 1)

for 씨앗 in range(5):
    _, _, _, 그냥 = train_test_split(X, y, test_size=0.2, random_state=씨앗)
    _, _, _, 층화 = train_test_split(X, y, test_size=0.2, random_state=씨앗, stratify=y)
    print(f"씨앗 {씨앗}: 시험 20명 중 양성  그냥 {그냥.sum()}명, stratify {층화.sum()}명")
