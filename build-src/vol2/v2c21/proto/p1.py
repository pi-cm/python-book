import sys, time
sys.path.insert(0, sys.argv[1])
import numpy as np, torch
from 맛집데이터 import 데이터_만들기, 시간으로_나누기
from 순위지표 import 평가셋_만들기, 평가하기
from 추천학습 import 행렬분해, 학습설정, 학습하기, 좋았던_쌍
t=time.time()
d = 데이터_만들기()
print("gen", time.time()-t, len(d.방문), d.방문.평점.value_counts().sort_index().to_dict())
학습, 검증, 시험 = 시간으로_나누기(d.방문)
print(len(학습), len(검증), len(시험))
import pandas as pd
v = 평가셋_만들기(학습, 검증, d.식당)
s = 평가셋_만들기(pd.concat([학습, 검증]), 시험, d.식당)
print("eval users", len(v.사용자), len(s.사용자), np.mean([len(a) for a in s.정답]))
cnt = np.bincount(학습.식당, minlength=400).astype(float)
for nm,셋 in [("val", v), ("test", s)]:
    rng=np.random.default_rng(0)
    print(nm, "rand", 평가하기(rng.random((len(셋.사용자),400)), 셋))
    print(nm, "pop", 평가하기(np.tile(cnt,(len(셋.사용자),1)), 셋))
    # area pop: user home area
    home = d.사용자.동네.to_numpy()[셋.사용자]
    area = d.식당.지역.to_numpy()
    sc = cnt[None,:] + 1e6*(area[None,:]==home[:,None])
    print(nm, "areapop", 평가하기(sc, 셋))
쌍 = 좋았던_쌍(학습)
후보 = torch.tensor(np.where(d.식당.개업일.to_numpy() < 300)[0])
for loss in ["bce","bpr"]:
    torch.manual_seed(0)
    m = 행렬분해(3000, 400, 32)
    def 검증(m):
        with torch.no_grad(): return 평가하기(m.모든_점수(torch.tensor(v.사용자)).numpy(), v)["NDCG@10"]
    t=time.time()
    h = 학습하기(m, 쌍, 후보, 학습설정(손실=loss, 에폭=int(sys.argv[2]) if len(sys.argv)>2 else 15), 검증)
    print(loss, time.time()-t, [round(x["검증"],4) for x in h])
    with torch.no_grad(): print(loss, "test", 평가하기(m.모든_점수(torch.tensor(s.사용자)).numpy(), s))
