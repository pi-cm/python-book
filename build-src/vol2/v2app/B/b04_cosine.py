import torch
import torch.nn.functional as F

a = torch.tensor([1.0, 1.0])
b = torch.tensor([10.0, 10.0])     # a와 방향이 같고 길이만 10배
c = torch.tensor([1.0, 0.0])       # a와 45도
d = torch.tensor([-1.0, -1.0])     # a와 정반대


def 코사인(x: torch.Tensor, y: torch.Tensor) -> float:
    """내적을 두 길이의 곱으로 나눈다."""
    return ((x @ y) / (x.norm() * y.norm())).item()


for 이름, v in [("b", b), ("c", c), ("d", d)]:
    print(f"a와 {이름}: 내적 {(a @ v).item():6.1f}  코사인 {코사인(a, v):+.4f}")
print("내장 함수(a와 c):", round(F.cosine_similarity(a, c, dim=0).item(), 4))

# 길이를 1로 맞춘(단위 벡터) 뒤 행렬 곱 한 번이면 모든 쌍의 코사인이 나온다
단위 = F.normalize(torch.stack([a, b, c, d]), dim=1)
for 줄 in (단위 @ 단위.T).tolist():
    print([f"{값:+.2f}" for 값 in 줄])
