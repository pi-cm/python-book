import torch

점수 = torch.tensor([1000.0, 999.0, 0.0])
지수 = torch.exp(점수)
print("그대로 exp:", 지수, "->", 지수 / 지수.sum())

# 가장 큰 값을 빼고 계산해도 결과는 같다 (모두에 같은 수를 빼도 소프트맥스는 그대로)
빼고 = torch.exp(점수 - 점수.max())
print("최댓값 빼기:", (빼고 / 빼고.sum()).round(decimals=4))
print("내장 함수  :", torch.softmax(점수, dim=0).round(decimals=4))
