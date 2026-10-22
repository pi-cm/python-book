import numpy as np
import torch

배열 = np.array([1.0, 2.0, 3.0])

복사본 = torch.tensor(배열)        # 새 그릇에 옮겨 담기 (복사)
공유본 = torch.from_numpy(배열)    # 같은 그릇을 함께 쓰기 (공유)

배열[0] = 100.0                    # 원래 NumPy 배열을 바꿔 보면?
print("NumPy  :", 배열)
print("복사본 :", 복사본)
print("공유본 :", 공유본)

print("다시 NumPy로:", 공유본.numpy())
