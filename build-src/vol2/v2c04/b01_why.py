import time
import torch

# 사진 한 장 크기의 숫자: 세로 1080 × 가로 1920 × 색 3개
리스트_사진 = [0.5] * (1080 * 1920 * 3)
텐서_사진 = torch.full((1080, 1920, 3), 0.5)

시작 = time.perf_counter()
밝게 = [값 * 1.2 for 값 in 리스트_사진]
리스트_시간 = time.perf_counter() - 시작

시작 = time.perf_counter()
밝게_텐서 = 텐서_사진 * 1.2
텐서_시간 = time.perf_counter() - 시작

print(f"숫자 개수: {len(리스트_사진):,}개")
print(f"리스트: {리스트_시간:.3f}초, 텐서: {텐서_시간:.4f}초")
print(f"텐서가 약 {리스트_시간 / 텐서_시간:.0f}배 빠름")
