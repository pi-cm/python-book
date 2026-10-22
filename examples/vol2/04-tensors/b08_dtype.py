# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.3 자료형 · manuscript-vol2/chapters/04-tensors.md:282]
import torch

a = torch.tensor([1, 2, 3])
b = torch.tensor([0.5, 0.5, 0.5])
print((a + b).dtype)              # 정수 + 실수 → 실수로 맞춰진다

print(torch.tensor([7, 8]) / 2)   # / 는 정수끼리여도 실수 결과
print(torch.tensor([7, 8]) // 2)  # // 는 몫, 정수 그대로

x = torch.tensor([1.5, 2.7])
print(x.int(), x.to(torch.int64).dtype)   # 실수 → 정수: 소수점 버림
print(x.half().dtype, x.double().dtype)   # float16, float64

print(torch.tensor(0.1) + torch.tensor(0.2))                # 화면에는 반올림해서 보인다
print((torch.tensor(0.1) + torch.tensor(0.2)).item())       # float32의 실제 값
print((torch.tensor(0.1, dtype=torch.float64)
       + torch.tensor(0.2, dtype=torch.float64)).item())    # float64의 실제 값
