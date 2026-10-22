# [2권 Chapter 16. GPU와 성능: 같은 모델을 더 빠르게, 더 가볍게 · 16.6 혼합 정밀도: 16비트로 계산하기 · manuscript-vol2/chapters/16-gpu-performance.md:549]
import torch

for 자료형 in [torch.float32, torch.float16, torch.bfloat16]:
    정보 = torch.finfo(자료형)                       # 자료형이 담을 수 있는 수의 범위
    print(f"{str(자료형):<15} 최대 {정보.max:8.2e} | 가장 작은 정규 수 {정보.tiny:8.2e}"
          f" | 1 옆의 간격 {정보.eps:8.2e}")

값 = torch.tensor([70000.0, 0.00000001, 1.001, 0.1])
for 자료형 in [torch.float32, torch.float16, torch.bfloat16]:
    바꾼_값 = 값.to(자료형).tolist()
    print(f"{str(자료형):<15}", " ".join(f"{v:>13.7g}" for v in 바꾼_값))
