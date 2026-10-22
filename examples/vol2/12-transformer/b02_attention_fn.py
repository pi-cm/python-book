# [2권 Chapter 12. 어텐션과 트랜스포머: 처음부터 직접 구현 · 12.1 어텐션: 부드럽게 꺼내는 딕셔너리 · manuscript-vol2/chapters/12-transformer.md:91]
import math

import torch


def 어텐션(q: torch.Tensor, k: torch.Tensor, v: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """질문 q마다 키 k와 닮은 정도를 재서, 그 비율대로 값 v를 섞는다."""
    점수 = q @ k.transpose(-2, -1) / math.sqrt(k.size(-1))   # (질문 수, 키 수)
    가중치 = 점수.softmax(dim=-1)                            # 질문마다 합이 1
    return 가중치 @ v, 가중치                                 # (질문 수, 값 차원)


torch.manual_seed(0)
torch.set_printoptions(precision=3)
q = torch.randn(2, 4)       # 질문 2개, 각각 숫자 4개
k = torch.randn(5, 4)       # 키 5개 (질문과 길이가 같아야 내적이 된다)
v = torch.randn(5, 3)       # 값 5개 (키와 개수가 같아야 한다), 각각 숫자 3개

출력, 가중치 = 어텐션(q, k, v)
print("가중치:", tuple(가중치.shape), "출력:", tuple(출력.shape))
print(가중치)
print("질문마다 가중치 합:", 가중치.sum(dim=-1))

# 같은 계산을 einsum으로: 사라지는 글자(d, k)가 곱하고 더해 없어지는 차원
점수 = torch.einsum("qd,kd->qk", q, k) / math.sqrt(4)
print(torch.allclose(torch.einsum("qk,kv->qv", 점수.softmax(dim=-1), v), 출력))
