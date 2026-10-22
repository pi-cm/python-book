# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.6 한꺼번에 계산하기 · manuscript-vol2/chapters/04-tensors.md:917]
import torch

점수 = torch.tensor([[80.0, 70.0],
                     [92.0, 88.0],
                     [75.0, 95.0]])

print(점수.sum(), 점수.mean())
print(점수.mean(dim=0))                # 세로로 접기: 과목별 평균
print(점수.mean(dim=1))                # 가로로 접기: 학생별 평균
print(점수.mean(dim=1, keepdim=True).shape)
최고 = 점수.max(dim=0)
print(최고.values, 최고.indices)       # 과목별 최고점과 그 학생 번호
print(점수.argmax(dim=1))              # 학생별로 더 잘한 과목
