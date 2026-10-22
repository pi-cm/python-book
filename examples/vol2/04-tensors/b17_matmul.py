# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.6 한꺼번에 계산하기 · manuscript-vol2/chapters/04-tensors.md:844]
import torch

# 학생 3명 × 과목 2개 점수, 과목별 반영 비율
점수 = torch.tensor([[80.0, 70.0],
                     [92.0, 88.0],
                     [75.0, 95.0]])
비율 = torch.tensor([0.4, 0.6])

print(점수 @ 비율)                     # (3, 2) @ (2,) → (3,)
print((점수 * 비율).sum(dim=1))        # 같은 계산을 풀어 쓰면

두_기준 = torch.tensor([[0.4, 0.5],
                        [0.6, 0.5]])   # 기준 A, 기준 B
print(점수 @ 두_기준)                  # (3, 2) @ (2, 2) → (3, 2)
