# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.1 텐서 만들기 · manuscript-vol2/chapters/04-tensors.md:152]
import torch

torch.manual_seed(42)
첫번째 = torch.rand(3)

torch.manual_seed(42)
torch.randn(5)                    # 중간에 다른 코드가 난수를 먼저 쓰면
두번째 = torch.rand(3)
print(첫번째)
print(두번째)                     # 씨앗이 같아도 결과가 달라진다

# 나만 쓰는 난수 생성기: 전역 난수와 따로 돈다
생성기 = torch.Generator().manual_seed(7)
print(torch.rand(3, generator=생성기))
torch.randn(5)                    # 전역 난수를 얼마나 쓰든
생성기 = torch.Generator().manual_seed(7)
print(torch.rand(3, generator=생성기))   # 생성기의 순서는 그대로

# 섞는 순서 정하기: 0~9를 무작위 순서로
print(torch.randperm(10, generator=torch.Generator().manual_seed(1)))
