# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.6 한꺼번에 계산하기 · manuscript-vol2/chapters/04-tensors.md:877]
import torch

점수 = torch.tensor([[80.0, 70.0],
                     [92.0, 88.0],
                     [75.0, 95.0]])          # (학생 s, 과목 k)
비율 = torch.tensor([0.4, 0.6])              # (과목 k)

print(torch.einsum("sk,k->s", 점수, 비율))   # 점수 @ 비율과 같다
print(torch.einsum("sk->ks", 점수))          # 전치: 글자 순서만 바꾸기
print(torch.einsum("sk->k", 점수))           # s가 사라짐 = sum(dim=0)

# 반 2개 × 학생 3명 × 과목 2개, 반마다 다른 반영 기준 2가지 (예제용)
반별점수 = torch.stack([점수, 점수 - 10])     # (b, s, k) = (2, 3, 2)
기준 = torch.tensor([[[0.4, 0.5], [0.6, 0.5]],
                     [[0.5, 0.3], [0.5, 0.7]]])   # (b, k, c) = (2, 2, 2)
결과 = torch.einsum("bsk,bkc->bsc", 반별점수, 기준)
print(결과.shape)
print(torch.allclose(결과, 반별점수 @ 기준))   # @도 앞 차원을 배치로 보고 똑같이 계산
