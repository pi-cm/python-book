# [2권 Chapter 7. 데이터 파이프라인: Dataset과 DataLoader · 들어가며: 주방은 재료를 한꺼번에 꺼내지 않습니다 · manuscript-vol2/chapters/07-data-pipeline.md:18]
import torch

한장 = torch.zeros(3, 224, 224)               # 컬러 사진 한 장 (색, 세로, 가로)
한장_바이트 = 한장.numel() * 한장.element_size()  # 숫자 개수 × 숫자 하나의 크기(float32 = 4바이트)
print(f"사진 한 장: 숫자 {한장.numel():,}개, {한장_바이트 / 1024**2:.2f}MB")

for 장수 in [1_000, 100_000, 1_000_000]:
    print(f"사진 {장수:>9,}장: {장수 * 한장_바이트 / 1024**3:8.1f}GB")
