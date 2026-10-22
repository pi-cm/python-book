import torch

기준 = torch.tensor([1.0, 0.0])
비교 = {
    "같은 방향": torch.tensor([2.0, 0.0]),
    "45도"     : torch.tensor([1.0, 1.0]),
    "직각"     : torch.tensor([0.0, 3.0]),
    "반대 방향": torch.tensor([-2.0, 0.0]),
}
for 이름, v in 비교.items():
    print(f"{이름}: 내적 {(기준 @ v).item():.1f}")
