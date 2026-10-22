# [2권 Chapter 12. 어텐션과 트랜스포머: 처음부터 직접 구현 · 12.4 마스크: 보면 안 되는 칸 가리기 · manuscript-vol2/chapters/12-transformer.md:283]
import math

import torch

torch.manual_seed(0)
torch.set_printoptions(precision=3)
# 7장의 패딩 배치: 진짜 글자 3개인 문장과 5개인 문장. 0번은 채운 칸
입력 = torch.tensor([[13, 22, 19,  0,  0],
                     [ 7, 14,  1, 25, 21]])
진짜 = 입력 != 0                                    # (2, 5) 진짜 글자 자리
x = torch.randn(2, 5, 4)                            # 글자마다 숫자 4개라고 하자
점수 = x @ x.transpose(-2, -1) / math.sqrt(4)      # (2, 5, 5)

# 키 쪽(열)이 채운 칸이면 -inf로: softmax에서 e^(-inf) = 0이 된다
가린_점수 = 점수.masked_fill(~진짜[:, None, :], float("-inf"))
가중치 = 가린_점수.softmax(dim=-1)
print("첫 문장의 가중치(채운 칸 열은 0):")
print(가중치[0])
print("줄마다 합:", 가중치[0].sum(dim=-1))

# 잘못된 방법: softmax를 먼저 하고 채운 칸을 0으로 지우면 합이 1이 아니다
틀린 = 점수.softmax(dim=-1) * 진짜[:, None, :]
print("softmax 뒤에 지우면 줄마다 합:", 틀린[0].sum(dim=-1))
