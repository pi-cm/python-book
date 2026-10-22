# [2권 Chapter 12. 어텐션과 트랜스포머: 처음부터 직접 구현 · 12.6 순서 알려 주기: 위치 정보 · manuscript-vol2/chapters/12-transformer.md:616]
import math

import torch
from torch import nn

torch.manual_seed(0)
torch.set_printoptions(precision=3)
글자_임베딩 = nn.Embedding(10, 4)           # 글자 10종류, 글자마다 숫자 4개 (학습되는 표)
번호들 = torch.tensor([[3, 7, 3]])          # 글자 번호 세 개 (첫째와 셋째가 같은 글자)
x = 글자_임베딩(번호들)
print("모양:", tuple(번호들.shape), "→", tuple(x.shape))
print(x[0].detach())
print("표의 3번 줄을 꺼낸 것과 같은가:", torch.equal(x[0, 0], 글자_임베딩.weight[3]))

# 위치 임베딩을 더하면 같은 글자라도 자리에 따라 다른 숫자가 된다
위치_임베딩 = nn.Embedding(8, 4)            # 위치 0~7, 위치마다 숫자 4개
x = x + 위치_임베딩(torch.arange(3))
print("위치를 더한 뒤 0번 == 2번 자리:", torch.allclose(x[0, 0], x[0, 2]))

# 12.3절의 실험을 다시: 순서를 섞으면 이제 결과가 달라진다
층 = nn.Linear(4, 4, bias=False)


def 셀프_어텐션(x: torch.Tensor) -> torch.Tensor:
    return (층(x) @ 층(x).transpose(-2, -1) / math.sqrt(4)).softmax(dim=-1) @ x


with torch.no_grad():
    섞은_번호 = 번호들[:, [1, 0, 2]]
    원래 = 셀프_어텐션(글자_임베딩(번호들) + 위치_임베딩(torch.arange(3)))
    섞음 = 셀프_어텐션(글자_임베딩(섞은_번호) + 위치_임베딩(torch.arange(3)))
print("위치가 있으면 섞은 결과가 원래를 섞은 것과 같은가:", torch.allclose(섞음, 원래[:, [1, 0, 2]]))
