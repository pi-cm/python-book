# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.4 인덱싱과 슬라이싱 · manuscript-vol2/chapters/04-tensors.md:475]
import torch

기온 = torch.tensor([[ 2.0, 13.5, 25.7, 15.0],
                     [ 4.5, 15.0, 25.0, 17.5],
                     [ 1.0, 14.0, 26.0, 15.5]])

# where(조건, 참일 때 값, 거짓일 때 값): 원본은 두고 새 텐서를 만든다
print(torch.where(기온 > 20, 1, 0))
print(torch.where(기온 < 5, 0.0, 기온))      # 5도 미만만 0, 나머지는 그대로

# clamp: 아래·위 한계를 벗어난 값을 한계에 붙인다
print(기온.clamp(min=5.0, max=20.0))
print(torch.tensor([-0.3, 0.5, 1.7]).clamp(0.0, 1.0))   # 0~1 사이로 묶기
print(torch.tensor([-2.0, 0.0, 3.0]).clamp(min=0.0))    # 음수만 0으로
