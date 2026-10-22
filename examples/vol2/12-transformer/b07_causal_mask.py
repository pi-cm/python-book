# [2권 Chapter 12. 어텐션과 트랜스포머: 처음부터 직접 구현 · 12.4 마스크: 보면 안 되는 칸 가리기 · manuscript-vol2/chapters/12-transformer.md:330]
import math

import torch

T = 5
보임 = torch.tril(torch.ones(T, T, dtype=torch.bool))    # 아래 삼각형: 나와 내 앞만 보임
print(보임.int())

torch.manual_seed(0)
torch.set_printoptions(precision=2)
x = torch.randn(1, T, 4)


def 인과_어텐션(x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    점수 = x @ x.transpose(-2, -1) / math.sqrt(x.size(-1))
    가중치 = 점수.masked_fill(~보임, float("-inf")).softmax(dim=-1)
    return 가중치 @ x, 가중치


출력, 가중치 = 인과_어텐션(x)
print(가중치[0])

# 마지막 글자를 바꿔도 앞 글자들의 출력은 그대로일까?
바꾼_x = x.clone()
바꾼_x[0, -1] = 100.0
바꾼_출력, _ = 인과_어텐션(바꾼_x)
print("앞 네 글자 출력이 같은가:", torch.allclose(출력[:, :4], 바꾼_출력[:, :4]))
print("마지막 글자 출력이 같은가:", torch.allclose(출력[:, 4], 바꾼_출력[:, 4]))
