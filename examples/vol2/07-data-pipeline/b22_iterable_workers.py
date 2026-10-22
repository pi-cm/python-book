# [2권 Chapter 7. 데이터 파이프라인: Dataset과 DataLoader · 7.10 num_workers와 병목 찾기 · manuscript-vol2/chapters/07-data-pipeline.md:1213]
from collections.abc import Iterator

from torch.utils.data import DataLoader, IterableDataset, get_worker_info


class 주문_흐름(IterableDataset):
    """주문 번호를 차례로 흘려보낸다. 나눠_읽기=True면 일꾼끼리 몫을 나눈다."""

    def __init__(self, 주문_수: int, 나눠_읽기: bool) -> None:
        self.주문_수 = 주문_수
        self.나눠_읽기 = 나눠_읽기

    def __iter__(self) -> Iterator[int]:
        정보 = get_worker_info()                 # 일꾼 안이면 (번호, 전체 수)를 알려 준다
        if not self.나눠_읽기 or 정보 is None:
            return iter(range(self.주문_수))
        # 일꾼 0은 0, 2, 4, ...  일꾼 1은 1, 3, 5, ... 처럼 건너뛰며 맡는다
        return iter(range(정보.id, self.주문_수, 정보.num_workers))


def main() -> None:
    for 나눠_읽기 in [False, True]:
        로더 = DataLoader(주문_흐름(6, 나눠_읽기), batch_size=None, num_workers=2)
        받은_것 = sorted(int(x) for x in 로더)
        print(f"나눠_읽기={나눠_읽기}: {받은_것}")


if __name__ == "__main__":
    main()
