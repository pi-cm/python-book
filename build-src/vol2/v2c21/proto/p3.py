import sys
sys.path.insert(0, sys.argv[1])
import numpy as np, torch, pandas as pd
from 맛집데이터 import 데이터_만들기, 시간으로_나누기, 음식들, 지역들
from 순위지표 import 평가셋_만들기, 평가하기
from 추천학습 import 행렬분해, 학습설정, 학습하기, 좋았던_쌍
d = 데이터_만들기(); 학습, 검증, 시험 = 시간으로_나누기(d.방문)
v = 평가셋_만들기(학습, 검증, d.식당)
쌍 = 좋았던_쌍(학습); 후보 = torch.tensor(np.where(d.식당.개업일.to_numpy() < 300)[0])
torch.manual_seed(0); m = 행렬분해(3000,400,32)
def 검증f(m):
    with torch.no_grad(): return 평가하기(m.모든_점수(torch.tensor(v.사용자)).numpy(), v)["NDCG@10"]
학습하기(m, 쌍, 후보, 학습설정(에폭=40), 검증f)
E = m.식당.weight.detach(); b = m.편향.weight.detach()[:,0]
old = np.where(d.식당.개업일<300)[0]
cnt = np.bincount(학습.식당, minlength=400)
print("bias vs log cnt corr", np.corrcoef(b.numpy()[old], np.log1p(cnt[old]))[0,1])
print("norm vs log cnt", np.corrcoef(E.norm(dim=1).numpy()[old], np.log1p(cnt[old]))[0,1])
En = E/E.norm(dim=1,keepdim=True)
r = d.식당
for q in [0, 5, 17]:
    sim = (En@En[q]).numpy(); sim[q]=-9; sim[r.개업일>=300]=-9
    top = np.argsort(-sim)[:5]
    print(r.loc[q, ["이름","가격대","숨은_매운맛","숨은_분위기"]].to_dict())
    print(r.loc[top, ["이름","가격대","숨은_매운맛","숨은_분위기"]].assign(유사도=sim[top]).round(2).to_string())
def r2(X, y, tr, te):
    X1 = torch.cat([X, torch.ones(len(X),1)],1)
    w = torch.linalg.lstsq(X1[tr], y[tr,None]).solution
    p = (X1[te]@w)[:,0]
    return 1 - ((y[te]-p)**2).sum()/((y[te]-y[te].mean())**2).sum()
tr, te = old[old%2==0], old[old%2==1]
onehot = torch.nn.functional.one_hot(torch.tensor(r.음식.to_numpy()), 8).float()
area1 = torch.nn.functional.one_hot(torch.tensor(r.지역.to_numpy()), 8).float()
feat = torch.cat([onehot, area1, torch.tensor(r.가격대.to_numpy())[:,None].float()],1)
for col in ["숨은_매운맛","숨은_분위기","숨은_품질"]:
    y = torch.tensor(r[col].to_numpy()).float()
    print(col, "features", round(r2(feat,y,tr,te).item(),3), "emb", round(r2(E,y,tr,te).item(),3), "emb+bias", round(r2(torch.cat([E,b[:,None]],1),y,tr,te).item(),3))
