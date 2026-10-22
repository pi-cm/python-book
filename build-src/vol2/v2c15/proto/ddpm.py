import math, time, sys
import torch
from torch import nn
from torchvision import datasets
import torch.nn.functional as F

dev = torch.device("mps")
torch.manual_seed(0)
ds = datasets.FashionMNIST("data", train=True, download=True)
X = (ds.data.float() / 255 * 2 - 1).unsqueeze(1).to(dev)
T = 1000
betas = torch.linspace(1e-4, 0.02, T, device=dev)
alphas = 1 - betas
abar = torch.cumprod(alphas, 0)

def temb(t, dim):
    half = dim // 2
    f = torch.exp(-math.log(10000) * torch.arange(half, device=t.device) / half)
    a = t.float()[:, None] * f[None]
    return torch.cat([a.sin(), a.cos()], 1)

class Block(nn.Module):
    def __init__(s, i, o, td):
        super().__init__()
        s.c1 = nn.Conv2d(i, o, 3, padding=1); s.n1 = nn.GroupNorm(8, o)
        s.t = nn.Linear(td, o)
        s.c2 = nn.Conv2d(o, o, 3, padding=1); s.n2 = nn.GroupNorm(8, o)
        s.skip = nn.Conv2d(i, o, 1) if i != o else nn.Identity()
    def forward(s, x, te):
        h = F.silu(s.n1(s.c1(x)))
        h = h + s.t(te)[:, :, None, None]
        h = F.silu(s.n2(s.c2(h)))
        return h + s.skip(x)

class UNet(nn.Module):
    def __init__(s, c=int(sys.argv[2]) if len(sys.argv)>2 else 32, td=128):
        super().__init__()
        s.td = td
        s.tm = nn.Sequential(nn.Linear(td, td), nn.SiLU(), nn.Linear(td, td))
        s.inp = nn.Conv2d(1, c, 3, padding=1)
        s.d1 = Block(c, c, td); s.down1 = nn.Conv2d(c, c, 4, 2, 1)
        s.d2 = Block(c, 2*c, td); s.down2 = nn.Conv2d(2*c, 2*c, 4, 2, 1)
        s.mid = Block(2*c, 2*c, td)
        s.up2 = nn.ConvTranspose2d(2*c, 2*c, 4, 2, 1); s.u2 = Block(4*c, 2*c, td)
        s.up1 = nn.ConvTranspose2d(2*c, c, 4, 2, 1); s.u1 = Block(2*c, c, td)
        s.out = nn.Conv2d(c, 1, 3, padding=1)
    def forward(s, x, t):
        te = s.tm(temb(t, s.td))
        h = s.inp(x)
        h1 = s.d1(h, te)
        h2 = s.d2(s.down1(h1), te)
        h = s.mid(s.down2(h2), te)
        h = s.u2(torch.cat([s.up2(h), h2], 1), te)
        h = s.u1(torch.cat([s.up1(h), h1], 1), te)
        return s.out(h)

m = UNet().to(dev)
print(sum(p.numel() for p in m.parameters()))
opt = torch.optim.Adam(m.parameters(), lr=2e-3)
B = 128
steps = int(sys.argv[1])
t0 = time.time()
for step in range(steps):
    idx = torch.randint(0, len(X), (B,), device=dev)
    x0 = X[idx]
    t = torch.randint(0, T, (B,), device=dev)
    eps = torch.randn_like(x0)
    ab = abar[t][:, None, None, None]
    xt = ab.sqrt() * x0 + (1 - ab).sqrt() * eps
    loss = F.mse_loss(m(xt, t), eps)
    opt.zero_grad(); loss.backward(); opt.step()
    if step % 500 == 0: print(step, loss.item(), time.time()-t0, flush=True)
print("train", time.time()-t0)
torch.save(m.state_dict(), "m.pt")
m.eval()
with torch.no_grad():
    x = torch.randn(64, 1, 28, 28, device=dev)
    for i in reversed(range(T)):
        t = torch.full((64,), i, device=dev)
        e = m(x, t)
        x = (x - betas[i] / (1 - abar[i]).sqrt() * e) / alphas[i].sqrt()
        if i > 0: x = x + betas[i].sqrt() * torch.randn_like(x)
print("total", time.time()-t0)
from torchvision.utils import save_image
save_image((x.clamp(-1,1)+1)/2, "samples.png", nrow=8)
