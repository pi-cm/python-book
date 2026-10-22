# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.5 모양 바꾸기 · manuscript-vol2/chapters/04-tensors.md:729]
import torch

사진 = torch.zeros(3, 224, 224)
묶음 = 사진.unsqueeze(0)            # 맨 앞에 크기 1인 차원 추가
print(묶음.shape)
print(묶음.squeeze(0).shape)        # 크기 1인 차원 빼기

a = torch.tensor([1, 2, 3])
b = torch.tensor([4, 5, 6])
print(torch.cat([a, b]))            # 이어 붙이기: 차원 수 그대로
print(torch.stack([a, b]))          # 쌓기: 새 차원이 생긴다
print(torch.stack([a, b]).shape, torch.stack([a, b], dim=1).shape)

print(torch.zeros(32, 3, 4, 4).flatten(start_dim=1).shape)   # 사진마다 한 줄로
