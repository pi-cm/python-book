# [2권 Chapter 7. 데이터 파이프라인: Dataset과 DataLoader · 7.9 불균형 데이터: WeightedRandomSampler · manuscript-vol2/chapters/07-data-pipeline.md:1010]
import torch
from torch.utils.data import DataLoader, TensorDataset, WeightedRandomSampler

# 예제용 불균형 데이터: 정상 950개, 불량 50개
정답 = torch.cat([torch.zeros(950, dtype=torch.long), torch.ones(50, dtype=torch.long)])
데이터 = TensorDataset(torch.arange(1000), 정답)        # 입력 자리에는 샘플 번호를 넣어 둔다


def 한_에폭_세기(로더: DataLoader) -> None:
    """한 에폭 동안 나온 클래스별 개수와, 불량 샘플이 몇 종류였는지 센다."""
    개수 = torch.zeros(2, dtype=torch.long)
    본_불량 = set()
    배치별_불량 = []
    for 번호, y in 로더:
        개수 += torch.bincount(y, minlength=2)
        본_불량.update(번호[y == 1].tolist())
        배치별_불량.append(int(y.sum()))
    print(f"  정상 {개수[0]}개, 불량 {개수[1]}개 (서로 다른 불량 샘플 {len(본_불량)}종)")
    print(f"  배치마다 불량 개수(앞 8배치): {배치별_불량[:8]}")


g = torch.Generator().manual_seed(0)
print("그냥 섞기:")
한_에폭_세기(DataLoader(데이터, batch_size=50, shuffle=True, generator=g))

클래스별_개수 = torch.bincount(정답)                    # [950, 50]
샘플_가중치 = 1.0 / 클래스별_개수[정답].float()          # 드문 클래스일수록 크게
print(f"가중치: 정상 {샘플_가중치[0]:.5f}, 불량 {샘플_가중치[-1]:.5f}")
샘플러 = WeightedRandomSampler(샘플_가중치, num_samples=len(데이터),
                              replacement=True, generator=g)
print("WeightedRandomSampler:")
한_에폭_세기(DataLoader(데이터, batch_size=50, sampler=샘플러))
