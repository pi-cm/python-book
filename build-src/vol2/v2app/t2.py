import torch
try:
    print(torch.ones(2).numpy())
except Exception as e:
    print(type(e).__name__, e)
