import torch

torch.manual_seed(42)             # 같은 씨앗이면 같은 난수가 나온다
print(torch.rand(2, 3))           # 0 이상 1 미만에서 고르게
print(torch.randn(2, 3))          # 평균 0, 표준편차 1인 정규분포
print(torch.randint(1, 7, (5,)))  # 주사위 다섯 번: 1 이상 7 미만 정수

torch.manual_seed(42)
print(torch.rand(2, 3))           # 씨앗을 다시 심으면 처음과 똑같다
