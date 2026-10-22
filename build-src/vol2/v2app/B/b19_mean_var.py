import torch

점수_a = torch.tensor([70.0, 71.0, 69.0, 70.0, 70.0])
점수_b = torch.tensor([50.0, 90.0, 60.0, 80.0, 70.0])
for 이름, x in [("A반", 점수_a), ("B반", 점수_b)]:
    평균 = x.mean()
    분산 = ((x - 평균) ** 2).mean()          # 평균에서 떨어진 거리의 제곱을 평균
    print(f"{이름} 평균 {평균.item():.1f}  분산 {분산.item():6.1f}  표준편차 {분산.sqrt().item():5.2f}")

print("torch.std 기본값  :", round(점수_b.std().item(), 2))            # n - 1로 나눔
print("correction=0     :", round(점수_b.std(correction=0).item(), 2))    # n으로 나눔
