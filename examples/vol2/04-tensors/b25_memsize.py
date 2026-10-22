# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.3 자료형 · manuscript-vol2/chapters/04-tensors.md:337]
import torch

MB = 1024 ** 2
사진묶음 = torch.zeros(32, 3, 224, 224)
print(사진묶음.element_size(), "바이트 ×", f"{사진묶음.numel():,}개")
print(f"{사진묶음.element_size() * 사진묶음.numel() / MB:.1f} MB")

for 자료형 in [torch.float64, torch.float32, torch.bfloat16, torch.int8]:
    t = torch.zeros(32, 3, 224, 224, dtype=자료형)
    크기 = t.element_size() * t.numel() / MB
    print(f"{str(자료형):15} 칸당 {t.element_size()}바이트 → {크기:6.1f} MB")

# 숫자 70억 개(7B 모델)를 float32로 담으면?
GB = 1024 ** 3
print(f"70억 × 4바이트 = {7_000_000_000 * 4 / GB:.1f} GB")
