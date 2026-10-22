# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.6 한꺼번에 계산하기 · manuscript-vol2/chapters/04-tensors.md:952]
import torch

점수 = torch.tensor([72.0, 95.0, 88.0, 60.0, 91.0, 79.0])
정렬 = 점수.sort(descending=True)
print(정렬.values)
print(정렬.indices)                 # 원래 몇 번째 학생이었는지
print(점수.argsort())               # 오름차순 순서(번호)만

상위 = 점수.topk(3)                 # 큰 값 3개만
print(상위.values, 상위.indices)

# 사진 2장의 클래스별 확률에서 장마다 상위 2개 후보
확률 = torch.tensor([[0.05, 0.60, 0.10, 0.25],
                     [0.40, 0.05, 0.35, 0.20]])
값, 번호 = 확률.topk(2, dim=1)
print(번호)
print(값)
정답 = torch.tensor([3, 1])
print("상위 2개 안에 정답이 있나:", (번호 == 정답.unsqueeze(1)).any(dim=1))
