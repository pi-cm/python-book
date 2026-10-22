# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.4 인덱싱과 슬라이싱 · manuscript-vol2/chapters/04-tensors.md:558]
import torch

정답 = torch.tensor([0, 1, 2, 1])

# scatter_: gather의 반대. 번호표가 가리키는 칸에 값을 써 넣는다
원핫 = torch.zeros(4, 3)
원핫.scatter_(dim=1, index=정답.unsqueeze(1), value=1.0)
print(원핫)
print(torch.nn.functional.one_hot(정답, num_classes=3))   # 같은 일을 하는 지름길

# 같은 칸에 여러 번 오면 더하기: 클래스별 개수 세기
개수 = torch.zeros(3).scatter_add_(0, 정답, torch.ones(4))
print(개수)
print(torch.bincount(정답))                                # 개수만 필요하면 이쪽
