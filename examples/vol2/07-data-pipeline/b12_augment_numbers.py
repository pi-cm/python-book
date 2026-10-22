# [2권 Chapter 7. 데이터 파이프라인: Dataset과 DataLoader · 7.6 transforms: 꺼낼 때 손질하기 · manuscript-vol2/chapters/07-data-pipeline.md:634]
import torch
from torchvision.transforms import v2

torch.manual_seed(0)
그림 = torch.arange(1, 13, dtype=torch.uint8).reshape(1, 3, 4)   # 흑백 1채널, 세로 3 × 가로 4
print(f"원본:\n{그림[0]}")

print(f"좌우 뒤집기:\n{v2.RandomHorizontalFlip(p=1.0)(그림)[0]}")
print(f"상하 뒤집기:\n{v2.RandomVerticalFlip(p=1.0)(그림)[0]}")

자르기 = v2.RandomCrop(size=(3, 4), padding=1)     # 테두리를 0으로 1칸 두른 뒤 원래 크기로 자르기
for i in range(2):
    print(f"무작위 자르기 {i + 1}:\n{자르기(그림)[0]}")

반반 = v2.RandomHorizontalFlip(p=0.5)
뒤집힌_횟수 = sum(int(not torch.equal(반반(그림), 그림)) for _ in range(1000))
print("p=0.5로 1000번 중 뒤집힌 횟수:", 뒤집힌_횟수)
