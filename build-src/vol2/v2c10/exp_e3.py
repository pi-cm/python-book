import time, sys, torch
from torch import nn
from torchvision import models
from 전이도구 import *
dev = 장치_고르기()
s=time.time()
Xtr,ytr = 유로샛_불러오기("학습", 50); Xva,yva = 유로샛_불러오기("검증", 100)
print("load", time.time()-s, Xtr.shape, Xva.shape)
va = 로더_만들기(Xva,yva)
def run(name, m, opt, ep, aug=True):
    torch.manual_seed(0)
    tr = 로더_만들기(Xtr,ytr,증강=aug,섞기=True)
    s=time.time()
    for e in range(ep):
        l=한_에폭_학습(m,tr,opt,dev)
    print(name, f"loss {l:.3f} train {정확도(m,로더_만들기(Xtr,ytr),dev):.3f} val {정확도(m,va,dev):.3f} {time.time()-s:.0f}s")
torch.manual_seed(0)
m=models.resnet18(num_classes=10).to(dev); run("scratch20", m, torch.optim.Adam(m.parameters(),1e-3), 20)
torch.manual_seed(0)
m=models.resnet18(weights="DEFAULT"); m.fc=nn.Linear(512,10); m.to(dev); run("ft1e-4", m, torch.optim.Adam(m.parameters(),1e-4), 8)
torch.manual_seed(0)
m=models.resnet18(weights="DEFAULT"); m.fc=nn.Linear(512,10); m.to(dev); run("ft1e-2", m, torch.optim.Adam(m.parameters(),1e-2), 8)
torch.manual_seed(0)
m=models.resnet18(weights="DEFAULT"); m.fc=nn.Linear(512,10); m.to(dev); run("ft1e-3", m, torch.optim.Adam(m.parameters(),1e-3), 8)
