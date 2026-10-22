# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.10 NumPy와 다른 점, 자주 만나는 오류 · manuscript-vol2/chapters/04-tensors.md:1223]
import numpy as np
import torch

a = np.array([[1.0, 2.0], [3.0, 4.0]])
t = torch.tensor([[1.0, 2.0], [3.0, 4.0]])

print(a.sum(axis=0), t.sum(dim=0))          # NumPy는 axis, PyTorch는 dim
print(np.concatenate([a, a]).shape, torch.cat([t, t]).shape)
print(a.astype(np.int64).dtype, t.to(torch.int64).dtype)
print(a.max(axis=1))
print(t.max(dim=1))                         # PyTorch는 값과 위치를 함께 준다

# 표준편차: 이름은 같은데 기본 계산이 다르다
값 = [2.0, 4.0, 4.0, 6.0]
print(np.std(값), torch.tensor(값).std())
print(np.std(값, ddof=1), torch.tensor(값).std(correction=0))   # 서로 맞추기
