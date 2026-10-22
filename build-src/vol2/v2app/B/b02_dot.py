import torch

a = torch.tensor([1.0, 2.0, 3.0])
b = torch.tensor([4.0, 5.0, 6.0])

print("같은 자리끼리 곱하기:", (a * b).tolist())
print("그걸 모두 더하기   :", (a * b).sum().item())   # 이것이 내적
print("@ 로 한 번에       :", (a @ b).item())
print("torch.dot          :", torch.dot(a, b).item())
