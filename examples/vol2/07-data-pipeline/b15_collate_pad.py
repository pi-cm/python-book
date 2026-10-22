# [2권 Chapter 7. 데이터 파이프라인: Dataset과 DataLoader · 7.7 collate_fn: 길이가 다른 샘플 묶기 · manuscript-vol2/chapters/07-data-pipeline.md:802]
import torch
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader

# 앞 블록의 리뷰 데이터셋이 돌려준 샘플 세 개를 그대로 옮겨 적었다
샘플들 = [(torch.tensor([13, 22, 19, 21]), 1),
         (torch.tensor([7, 14, 1, 25, 21]), 0),
         (torch.tensor([10, 1, 20, 3, 1, 17, 19, 21]), 1)]


def 패딩_묶기(배치: list[tuple[torch.Tensor, int]]) -> dict[str, torch.Tensor]:
    """길이가 다른 문장들을 가장 긴 문장에 맞춰 0으로 채워 묶는다."""
    문장들 = [문장 for 문장, _ in 배치]
    return {
        "입력": pad_sequence(문장들, batch_first=True, padding_value=0),
        "길이": torch.tensor([len(문장) for 문장 in 문장들]),
        "정답": torch.tensor([라벨 for _, 라벨 in 배치]),
    }


배치 = 패딩_묶기(샘플들)                    # collate_fn은 그냥 함수라 직접 불러 볼 수 있다
print(배치["입력"])
print("길이:", 배치["길이"].tolist(), "정답:", 배치["정답"].tolist())
print("진짜 글자 자리(마스크):")
print((배치["입력"] != 0).int())

로더 = DataLoader(샘플들, batch_size=2, collate_fn=패딩_묶기)   # 리스트도 데이터셋이 된다
for 배치 in 로더:
    print(tuple(배치["입력"].shape), 배치["길이"].tolist())
