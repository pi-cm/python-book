# [2권 Chapter 7. 데이터 파이프라인: Dataset과 DataLoader · 7.1 Dataset: 번호를 주면 샘플 하나를 주는 약속 · manuscript-vol2/chapters/07-data-pipeline.md:60]
from torch.utils.data import Dataset


class 제곱수_데이터셋(Dataset):
    """0부터 n-1까지의 수와 그 제곱을 (입력, 정답) 짝으로 돌려준다."""

    def __init__(self, n: int) -> None:
        self.n = n                         # 재료 목록만 기억해 둔다

    def __len__(self) -> int:
        return self.n                      # 샘플이 모두 몇 개인가

    def __getitem__(self, i: int) -> tuple[int, int]:
        if i >= self.n:
            raise IndexError(f"{i}번 샘플은 없습니다")
        print(f"  ({i}번 샘플을 지금 만듭니다)")
        return i, i * i                    # i번 샘플 하나를 그때 만들어 돌려준다


데이터 = 제곱수_데이터셋(4)
print("샘플 수:", len(데이터))
print("3번 샘플:", 데이터[3])
for 입력, 정답 in 데이터:
    print("반복:", 입력, 정답)
