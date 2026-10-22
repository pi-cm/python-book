import torch

정답 = torch.tensor([3.0, 5.0, 2.0, 7.0])
예측 = torch.tensor([2.5, 5.0, 4.0, 8.0])
오차 = 예측 - 정답
print("오차      :", 오차.tolist())
print("MAE  (절댓값 평균)       :", 오차.abs().mean().item())
print("MSE  (제곱 평균)         :", (오차 ** 2).mean().item())
print("RMSE (MSE의 제곱근)      :", round((오차 ** 2).mean().sqrt().item(), 4))
