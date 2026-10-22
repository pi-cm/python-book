# [2권 Chapter 7. 데이터 파이프라인: Dataset과 DataLoader · 7.7 collate_fn: 길이가 다른 샘플 묶기 · manuscript-vol2/chapters/07-data-pipeline.md:859]
import torch
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader

torch.manual_seed(0)
# 예제용: 길이가 3~60글자로 제각각인 문장 1,000개 (글자 번호는 1~9)
문장들 = [torch.randint(1, 10, (int(n),)) for n in torch.randint(3, 61, (1000,))]


def 패딩_묶기(배치: list[torch.Tensor]) -> torch.Tensor:
    return pad_sequence(배치, batch_first=True, padding_value=0)


def 패딩_비율(로더: DataLoader) -> float:
    """배치에 들어간 칸 중 0으로 채운 칸의 비율."""
    전체 = 빈칸 = 0
    for 배치 in 로더:
        전체 += 배치.numel()
        빈칸 += (배치 == 0).sum().item()
    return 빈칸 / 전체


g = torch.Generator().manual_seed(0)
그냥 = DataLoader(문장들, batch_size=32, shuffle=True, collate_fn=패딩_묶기, generator=g)
print(f"그냥 섞었을 때 패딩 비율: {패딩_비율(그냥):.1%}")

# 길이순으로 줄 세운 뒤 32개씩 끊고, 묶음의 순서만 섞는다
길이순 = sorted(range(len(문장들)), key=lambda i: len(문장들[i]))
묶음들 = [길이순[i:i + 32] for i in range(0, len(길이순), 32)]
묶음들 = [묶음들[i] for i in torch.randperm(len(묶음들), generator=g).tolist()]
비슷한_길이끼리 = DataLoader(문장들, batch_sampler=묶음들, collate_fn=패딩_묶기)
print(f"비슷한 길이끼리 묶었을 때: {패딩_비율(비슷한_길이끼리):.1%}")
print("배치 수:", len(그냥), len(비슷한_길이끼리))
