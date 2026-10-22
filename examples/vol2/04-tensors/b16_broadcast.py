# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.6 한꺼번에 계산하기 · manuscript-vol2/chapters/04-tensors.md:793]
import torch

# 학생 3명 × 과목 2개 점수
점수 = torch.tensor([[80.0, 70.0],
                     [92.0, 88.0],
                     [75.0, 95.0]])

print(점수 + 5)                              # 모두에게 5점
과목별_보너스 = torch.tensor([3.0, 10.0])     # 국어 +3, 수학 +10
print(점수 + 과목별_보너스)                   # (3, 2) + (2,) → (3, 2)

학생별_보너스 = torch.tensor([[1.0], [2.0], [3.0]])   # (3, 1)
print(점수 + 학생별_보너스)                            # (3, 2) + (3, 1) → (3, 2)

try:
    점수 + torch.tensor([1.0, 2.0, 3.0])               # (3, 2) + (3,)
except RuntimeError as e:
    print("오류:", e)
