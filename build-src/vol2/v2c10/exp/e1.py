import time, torch
from torch import nn
from torchvision import datasets, models
from torchvision.transforms import v2
torch.manual_seed(0)
ds = datasets.EuroSAT("data")
t = torch.tensor(ds.targets)
g = torch.Generator().manual_seed(0)
def pick(n_per, offset):
    idx=[]
    for k in range(10):
        ii=(t==k).nonzero().flatten()
        p=ii[torch.randperm(len(ii),generator=torch.Generator().manual_seed(k))]
        idx += p[offset:offset+n_per].tolist()
    return idx
tr = pick(50,0); te = pick(100,1000)
w = models.ResNet18_Weights.DEFAULT
m = models.resnet18(weights=w); m.fc = nn.Identity(); m.eval()
for size in [64, 112, 224]:
    tf = v2.Compose([v2.ToImage(), v2.Resize(size), v2.ToDtype(torch.float32, scale=True), v2.Normalize(w.transforms().mean, w.transforms().std)])
    def feats(idx):
        X = torch.stack([tf(ds[i][0]) for i in idx]); 
        with torch.no_grad(): return torch.cat([m(X[i:i+100]) for i in range(0,len(X),100)])
    s=time.time(); Ftr=feats(tr); Fte=feats(te); el=time.time()-s
    ytr=t[tr]; yte=t[te]
    head=nn.Linear(512,10); opt=torch.optim.Adam(head.parameters(),1e-3)
    for ep in range(200):
        opt.zero_grad(); l=nn.functional.cross_entropy(head(Ftr),ytr); l.backward(); opt.step()
    acc=(head(Fte).argmax(1)==yte).float().mean().item()
    print(size, f"{el:.1f}s", acc)
