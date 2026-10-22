import time, torch
from torch import nn
from torchvision import models
for dev in ["cpu","mps"]:
    for size in [64,112]:
        m = models.resnet18(num_classes=10).to(dev); opt=torch.optim.Adam(m.parameters(),1e-3)
        x=torch.randn(64,3,size,size,device=dev); y=torch.randint(0,10,(64,),device=dev)
        for i in range(2):
            opt.zero_grad(); nn.functional.cross_entropy(m(x),y).backward(); opt.step()
        if dev=="mps": torch.mps.synchronize()
        s=time.time()
        for i in range(5):
            opt.zero_grad(); nn.functional.cross_entropy(m(x),y).backward(); opt.step()
        if dev=="mps": torch.mps.synchronize()
        print(dev,size,f"{(time.time()-s)/5/64*1000:.2f} ms/img")
