# [2권 Chapter 7. 데이터 파이프라인: Dataset과 DataLoader · 7.6 transforms: 꺼낼 때 손질하기 · manuscript-vol2/chapters/07-data-pipeline.md:564]
import numpy as np
import torch
from PIL import Image
from torchvision.transforms import v2

# 세로 2 × 가로 3짜리 아주 작은 컬러 그림 (예제용 숫자)
배열 = np.array([[[255, 0, 0], [0, 255, 0], [0, 0, 255]],
                 [[255, 255, 255], [128, 128, 128], [0, 0, 0]]], dtype=np.uint8)
그림 = Image.fromarray(배열)

텐서 = v2.ToImage()(그림)                                  # PIL → (색, 세로, 가로) 텐서
print("ToImage :", tuple(텐서.shape), 텐서.dtype)
print(텐서[0])                                              # 빨강 채널만
실수 = v2.ToDtype(torch.float32, scale=True)(텐서)          # 0~255 → 0~1
print("ToDtype :", 실수.dtype)
print(실수[0])
정규화 = v2.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])(실수)
print("Normalize:")
print(정규화[0])

한번에 = v2.Compose([v2.ToImage(), v2.ToDtype(torch.float32, scale=True),
                    v2.Normalize(mean=[0.5] * 3, std=[0.5] * 3)])
print("Compose와 같은가:", torch.equal(한번에(그림), 정규화))
