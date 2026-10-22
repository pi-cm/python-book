# [2권 부록 B. 꼭 필요한 수학 직관 · B.2 행렬 곱과 모양 규칙 · manuscript-vol2/appendix/B-math-intuition.md:177]
import torch

x = torch.tensor([[1.0, 2.0, 3.0],
                  [0.0, 1.0, 0.0]])      # 샘플 2개, 특성 3개
W = torch.tensor([[1.0, 0.0],
                  [0.0, 1.0],
                  [1.0, 1.0]])           # 특성 3개 -> 출력 2개

결과 = x @ W
print(결과)
# 결과[i, j]는 x의 i번째 줄과 W의 j번째 열의 내적
print("손으로 [0, 1]:", (x[0] @ W[:, 1]).item())
