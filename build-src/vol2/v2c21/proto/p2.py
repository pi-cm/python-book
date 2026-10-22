import sys, time
sys.path.insert(0, sys.argv[1])
import numpy as np, torch, pandas as pd
from 맛집데이터 import 데이터_만들기, 시간으로_나누기
from 순위지표 import 평가셋_만들기, 평가하기, recall_at_k, ndcg_at_k
from 추천학습 import 행렬분해, 학습설정, 학습하기, 좋았던_쌍
from 투타워 import 투타워
d = 데이터_만들기()
학습, 검증, 시험 = 시간으로_나누기(d.방문)
v = 평가셋_만들기(학습, 검증, d.식당)
s = 평가셋_만들기(pd.concat([학습, 검증]), 시험, d.식당)
쌍 = 좋았던_쌍(학습)
후보 = torch.tensor(np.where(d.식당.개업일.to_numpy() < 300)[0])
EP=int(sys.argv[2]); P=float(sys.argv[3]); LR=float(sys.argv[4]); WD=float(sys.argv[5])
models={}
for name in ["mf","tt"]:
    torch.manual_seed(0)
    m = 행렬분해(3000,400,32) if name=="mf" else 투타워(d.사용자, d.식당, 32, P)
    def 검증f(m):
        with torch.no_grad(): return 평가하기(m.모든_점수(torch.tensor(v.사용자)).numpy(), v)["NDCG@10"]
    t=time.time()
    h = 학습하기(m, 쌍, 후보, 학습설정(에폭=EP, 학습률=LR if name=="tt" else 0.005, 가중치_감쇠=WD if name=="tt" else 1e-4), 검증f)
    print(name, round(time.time()-t,1), [round(x["검증"],4) for x in h][::3])
    with torch.no_grad(): print(name, "test", 평가하기(m.모든_점수(torch.tensor(s.사용자)).numpy(), s))
    models[name]=m
# cold items: test users who had good visit at new restaurant (open>=300) not seen before
new = np.where(d.식당.개업일.to_numpy()>=300)[0]
이전 = pd.concat([학습, 검증]); 
좋 = 시험[(시험.평점>=3)&(시험.식당.isin(new))]
가본 = 이전.groupby("사용자").식당.apply(set)
rows=[]
for u,g in 좋.groupby("사용자").식당:
    if u in 가본.index and u < 2700:
        ans=set(g)-가본[u]
        if ans: rows.append((u,ans))
print("cold-item users", len(rows))
def evalnew(scorefn, k=5):
    R=[];N=[]
    for u,ans in rows:
        sc = scorefn(u)  # scores over new items
        order = new[np.argsort(-sc, kind="stable")]
        R.append(recall_at_k(list(order),ans,k)); N.append(ndcg_at_k(list(order),ans,k))
    return round(np.mean(R),4), round(np.mean(N),4)
rng=np.random.default_rng(0)
print("rand", evalnew(lambda u: rng.random(len(new))))
home=d.사용자.동네.to_numpy(); area=d.식당.지역.to_numpy()
print("home area", evalnew(lambda u: (area[new]==home[u]).astype(float)+rng.random(len(new))*1e-3))
mf=models["mf"]; tt=models["tt"]
with torch.no_grad():
    U=mf.사용자_벡터(torch.arange(3000)); I=mf.식당_벡터(torch.arange(400))
    print("mf raw", evalnew(lambda u: (U[u]@I[new].T).numpy()))
    # mf with feature-average
    old=np.where(d.식당.개업일.to_numpy()<300)[0]
    I2=I.clone(); cu=d.식당.음식.to_numpy()
    for j in new:
        same=old[(area[old]==area[j])&(cu[old]==cu[j])]
        if len(same)==0: same=old[area[old]==area[j]]
        I2[j]=I[same].mean(0)
    print("mf avg", evalnew(lambda u: (U[u]@I2[new].T).numpy()))
    tt.eval()
    TU=tt.사용자_벡터(torch.arange(3000)); TI=tt.식당_벡터(torch.tensor(new), 번호_쓰기=False)
    print("tt", evalnew(lambda u: (TU[u]@TI.T).numpy()))
# cold users: no train visits
cold = np.setdiff1d(np.arange(3000), 학습.사용자.unique())
print("cold users", len(cold))
cs = 평가셋_만들기(pd.concat([학습, 검증]), 시험, d.식당)  # only those with prior visits in val
# include cold users with zero prior: build manually
가본2 = 이전.groupby("사용자").식당.apply(set)
좋2 = 시험[시험.평점>=3]
cu_rows=[]
for u,g in 좋2[좋2.사용자.isin(cold)].groupby("사용자").식당:
    ans=set(g)-가본2.get(u,set())
    if ans: cu_rows.append((u,ans,가본2.get(u,set())))
print("cold user eval", len(cu_rows), np.mean([len(h) for _,_,h in cu_rows]))
cnt=np.bincount(이전.식당, minlength=400).astype(float)
opened = d.식당.개업일.to_numpy()<=364
def evalcu(scorefn,k=10):
    R=[];N=[]
    for u,ans,hist in cu_rows:
        sc=scorefn(u,hist).astype(float); sc[~opened]=-np.inf; sc[list(hist)]=-np.inf
        order=list(np.argsort(-sc,kind="stable")[:k]); R.append(recall_at_k(order,ans,k)); N.append(ndcg_at_k(order,ans,k))
    return round(np.mean(R),4), round(np.mean(N),4)
print("pop", evalcu(lambda u,h: cnt))
print("areapop", evalcu(lambda u,h: cnt+1e6*(area==home[u])))
with torch.no_grad():
    TIall = tt.식당_벡터(torch.arange(400)); 
    TIall[new] = tt.식당_벡터(torch.tensor(new), 번호_쓰기=False)
    print("tt unknown user", evalcu(lambda u,h: (tt.사용자_벡터(torch.tensor([u]),번호_쓰기=False)[0]@TIall.T).numpy()))
    def foldin(u,h):
        base = tt.사용자_벡터(torch.tensor([u]),번호_쓰기=False)[0]
        if not h: return (base@TIall.T).numpy()
        hv = TIall[list(h)].mean(0)
        return ((base+hv)@TIall.T).numpy()  # crude
    print("tt foldin", evalcu(foldin))
print("---- cold user variants")
with torch.no_grad():
    for nm, IV in [("mf", I2), ("tt", TIall)]:
        IVn = IV/IV.norm(dim=1,keepdim=True)
        sim = (IVn@IVn.T).numpy()
        base = np.log1p(cnt)
        for lam in [0, 1, 2, 4]:
            def f(u,h):
                a = base + 3.0*(area==home[u])
                if h: a = a + lam*sim[list(h)].mean(0)
                return a
            print(nm, lam, evalcu(f))
        print(nm, "pure sim", evalcu(lambda u,h: sim[list(h)].mean(0) if h else cnt+1e6*(area==home[u])))
