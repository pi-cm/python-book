# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.4 인덱싱과 슬라이싱 · manuscript-vol2/chapters/04-tensors.md:444]
import torch

원본 = torch.arange(6)
조각 = 원본[2:5]          # 슬라이싱은 복사하지 않는다
조각[0] = 100
print("조각:", 조각)
print("원본:", 원본)       # 원본도 바뀌었다!

안전 = 원본[2:5].clone()   # 따로 쓰고 싶으면 clone()
안전[0] = -1
print("원본:", 원본)       # 이번에는 그대로
