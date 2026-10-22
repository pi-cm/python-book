# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.6 한꺼번에 계산하기 · manuscript-vol2/chapters/04-tensors.md:768]
import torch

국어 = torch.tensor([80.0, 92.0, 75.0])
수학 = torch.tensor([70.0, 88.0, 95.0])

print(국어 + 수학)          # 같은 자리끼리 더하기
print((국어 + 수학) / 2)    # 평균
print(국어 > 수학)          # 같은 자리끼리 비교
print(torch.sqrt(국어))     # 함수도 칸마다
