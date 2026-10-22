import torch

z = torch.tensor([-4.0, -1.0, 0.0, 1.0, 4.0])
print("시그모이드       :", [f"{p:.4f}" for p in torch.sigmoid(z).tolist()])
print("1 / (1 + exp(-z)):", [f"{p:.4f}" for p in (1 / (1 + torch.exp(-z))).tolist()])

# 두 칸 소프트맥스 [z, 0]의 첫 칸 = 시그모이드(z)
두칸 = torch.stack([z, torch.zeros_like(z)], dim=1)
print("두 칸 소프트맥스 :", [f"{p:.4f}" for p in torch.softmax(두칸, dim=1)[:, 0].tolist()])
