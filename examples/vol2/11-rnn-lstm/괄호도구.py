# [2권 Chapter 11. RNN과 LSTM: 순서가 있는 데이터 · 11.3 순서를 알아야 풀리는 문제: 괄호 짝 맞추기 · manuscript-vol2/chapters/11-rnn-lstm.md:271]
"""11장 괄호 실험에서 함께 쓰는 데이터 도구."""
import random

import torch
from torch.nn.utils.rnn import pad_sequence


def 짝맞나(괄호: str) -> bool:
    """여는 괄호보다 닫는 괄호가 먼저 많아지는 순간이 없고, 끝에서 개수가 같으면 짝이 맞다."""
    깊이 = 0
    for 글자 in 괄호:
        깊이 += 1 if 글자 == "(" else -1
        if 깊이 < 0:
            return False
    return 깊이 == 0


def 괄호_만들기(개수: int, 길이들: list[int], 씨앗: int) -> tuple[list[str], torch.Tensor]:
    """짝이 맞는 괄호와 맞지 않는 괄호를 반반 만든다. 두 쪽 모두 '('와 ')'의 개수는 같다."""
    rng = random.Random(씨앗)
    괄호들 = []
    while len(괄호들) < 개수:
        길이 = rng.choice(길이들)
        글자들 = list("(" * (길이 // 2) + ")" * (길이 // 2))
        rng.shuffle(글자들)
        if not 짝맞나(글자들):
            continue                                 # 먼저 짝이 맞는 괄호를 하나 얻고
        if len(괄호들) % 2 == 1:                     # 홀수 번째는 두 글자를 맞바꿔 짝을 깬다
            while True:
                i, j = rng.sample(range(길이), 2)
                바꾼 = 글자들.copy()
                바꾼[i], 바꾼[j] = 바꾼[j], 바꾼[i]
                if not 짝맞나(바꾼):
                    break
            글자들 = 바꾼
        괄호들.append("".join(글자들))
    정답 = torch.tensor([int(짝맞나(괄호)) for 괄호 in 괄호들])
    return 괄호들, 정답


def 원핫으로(괄호들: list[str]) -> tuple[torch.Tensor, torch.Tensor]:
    """'('는 1번, ')'는 2번, 빈칸(패딩)은 0번 칸이 1인 원-핫 텐서와 길이를 돌려준다."""
    번호들 = [torch.tensor([1 if 글자 == "(" else 2 for 글자 in 괄호]) for 괄호 in 괄호들]
    채운 = pad_sequence(번호들, batch_first=True, padding_value=0)
    길이 = torch.tensor([len(괄호) for 괄호 in 괄호들])
    return torch.nn.functional.one_hot(채운, 3).float(), 길이
