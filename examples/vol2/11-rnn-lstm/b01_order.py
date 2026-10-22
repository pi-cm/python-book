# [2권 Chapter 11. RNN과 LSTM: 순서가 있는 데이터 · 들어가며: 순서를 바꾸면 뜻이 바뀝니다 · manuscript-vol2/chapters/11-rnn-lstm.md:18]
from collections import Counter

import torch

리뷰1 = "가격은 별로지만 맛은 최고"
리뷰2 = "맛은 별로지만 가격은 최고"

# 글자마다 몇 번 나왔는지만 센다: 어느 글자가 먼저 왔는지는 버린다
print(Counter(리뷰1) == Counter(리뷰2))

글자들 = sorted(set(리뷰1))
번호 = {글자: i for i, 글자 in enumerate(글자들)}


def 개수_벡터(문장: str) -> torch.Tensor:
    """문장을 글자 종류별 개수로 바꾼다."""
    v = torch.zeros(len(글자들))
    for 글자 in 문장:
        v[번호[글자]] += 1
    return v


print(torch.equal(개수_벡터(리뷰1), 개수_벡터(리뷰2)))

# 숫자 줄도 마찬가지: 닷새 동안의 주가 (예제용 숫자)
오르는_중 = torch.tensor([100.0, 102.0, 105.0, 109.0, 114.0])
내리는_중 = 오르는_중.flip(0)                # 같은 숫자를 거꾸로
print(오르는_중.mean().item(), 내리는_중.mean().item())
print(오르는_중.std().item() == 내리는_중.std().item())
print("마지막 날 - 첫날:", (오르는_중[-1] - 오르는_중[0]).item(),
      (내리는_중[-1] - 내리는_중[0]).item())
