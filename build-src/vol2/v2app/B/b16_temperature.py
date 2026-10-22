import torch

로짓 = torch.tensor([2.0, 1.0, 0.1])
for 온도 in [0.5, 1.0, 2.0]:
    print(f"온도 {온도}:", [f"{p:.3f}" for p in torch.softmax(로짓 / 온도, dim=0).tolist()])
