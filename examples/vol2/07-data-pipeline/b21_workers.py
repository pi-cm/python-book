# [2권 Chapter 7. 데이터 파이프라인: Dataset과 DataLoader · 7.10 num_workers와 병목 찾기 · manuscript-vol2/chapters/07-data-pipeline.md:1143]
import time

import torch
from torch.utils.data import DataLoader, Dataset

읽기_시간 = 0.01      # 샘플 하나를 디스크에서 읽고 푸는 데 10ms 걸린다고 치자
계산_시간 = 0.05      # 배치 하나로 모델을 학습시키는 데 50ms 걸린다고 치자


class 느린_데이터셋(Dataset):
    """꺼낼 때마다 읽기_시간만큼 기다리는 데이터셋 (디스크 읽기 흉내)."""

    def __len__(self) -> int:
        return 160

    def __getitem__(self, i: int) -> torch.Tensor:
        time.sleep(읽기_시간)
        return torch.full((3, 32, 32), float(i))


def 한_에폭(로더: DataLoader) -> tuple[float, float]:
    """한 에폭 전체 시간과, 그중 다음 배치를 기다린 시간을 잰다."""
    대기 = 0.0
    시작 = time.perf_counter()
    반복자 = iter(로더)
    while True:
        t = time.perf_counter()
        배치 = next(반복자, None)                # 다음 배치가 올 때까지 기다린다
        대기 += time.perf_counter() - t
        if 배치 is None:
            break
        time.sleep(계산_시간)                    # 학습 계산 흉내
    return time.perf_counter() - 시작, 대기


def main() -> None:
    for 일꾼 in [0, 2, 4]:
        로더 = DataLoader(느린_데이터셋(), batch_size=16, num_workers=일꾼,
                         persistent_workers=일꾼 > 0)   # 에폭이 끝나도 일꾼을 살려 둔다
        첫_전체, _ = 한_에폭(로더)
        전체, 대기 = 한_에폭(로더)
        print(f"num_workers={일꾼}: 첫 에폭 {첫_전체:.1f}초, 둘째 에폭 {전체:.1f}초 "
              f"(그중 데이터 대기 {대기 / 전체:.0%})")


if __name__ == "__main__":
    main()
