# [2권 Chapter 2. 데이터 준비: 모델에 넣기 전에 할 일 · 2.5 범주형 인코딩: 글자를 숫자로 · manuscript-vol2/chapters/02-data-preparation.md:606]
import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder

rng = np.random.default_rng(0)
# 동네 이름 200가지가 섞인 주소 1000건 (예제용). 앞 번호일수록 흔하다
비율 = 1 / np.arange(1, 201)
동네 = pd.DataFrame({"동네": rng.choice([f"동{i:03d}" for i in range(200)], 1000,
                                       p=비율 / 비율.sum())})
print("서로 다른 동네:", 동네["동네"].nunique(), "곳")

전부 = OneHotEncoder(handle_unknown="ignore").fit(동네)
print("그냥 원-핫:", len(전부.get_feature_names_out()), "열")

묶기 = OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=20).fit(동네)
이름 = 묶기.get_feature_names_out()
print("20번 미만은 묶기:", len(이름), "열 →", 이름[:3].tolist(), "...", 이름[-1])
