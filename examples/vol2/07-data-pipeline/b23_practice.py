# [2권 Chapter 7. 데이터 파이프라인: Dataset과 DataLoader · 7.11 실습: 도형 그림 파이프라인 한 바퀴 · manuscript-vol2/chapters/07-data-pipeline.md:1277]
from pathlib import Path

import torch
from torch.utils.data import DataLoader, Subset, WeightedRandomSampler
from torchvision.datasets import ImageFolder
from torchvision.transforms import v2

from 도형_만들기 import 도형_폴더_만들기

뿌리 = Path("data/shapes_practice")
씨앗 = 42


def 학습_검증_번호(전체_수: int, 검증_비율: float = 0.2) -> tuple[list[int], list[int]]:
    """씨앗을 고정해 섞은 번호를 학습용과 검증용으로 자른다."""
    번호 = torch.randperm(전체_수, generator=torch.Generator().manual_seed(씨앗)).tolist()
    검증_수 = int(전체_수 * 검증_비율)
    return 번호[검증_수:], 번호[:검증_수]


def 채널_통계(데이터: Subset) -> tuple[list[float], list[float]]:
    """학습용 그림만으로 색 채널별 평균과 표준편차를 구한다."""
    모두 = torch.stack([그림 for 그림, _ in 데이터])            # (N, 3, 32, 32)
    return 모두.mean(dim=(0, 2, 3)).tolist(), 모두.std(dim=(0, 2, 3)).tolist()


def 로더_만들기() -> tuple[DataLoader, DataLoader, list[str]]:
    학습_번호, 검증_번호 = 학습_검증_번호(len(ImageFolder(뿌리)))
    기본 = [v2.ToImage(), v2.ToDtype(torch.float32, scale=True)]
    평균, 표준편차 = 채널_통계(Subset(ImageFolder(뿌리, transform=v2.Compose(기본)), 학습_번호))
    print("학습용 채널 평균:", [round(m, 3) for m in 평균])

    정규화 = v2.Normalize(mean=평균, std=표준편차)
    학습_변환 = v2.Compose([v2.ToImage(),
                          v2.RandomHorizontalFlip(p=0.5),
                          v2.RandomCrop(size=32, padding=3, fill=255),   # 흰 바탕색으로 테두리
                          v2.ToDtype(torch.float32, scale=True), 정규화])
    검증_변환 = v2.Compose(기본 + [정규화])                                # 증강 없음

    학습 = Subset(ImageFolder(뿌리, transform=학습_변환), 학습_번호)
    검증 = Subset(ImageFolder(뿌리, transform=검증_변환), 검증_번호)

    정답 = torch.tensor(학습.dataset.targets)[학습_번호]                  # 학습용 샘플의 정답들
    가중치 = 1.0 / torch.bincount(정답)[정답].float()
    샘플러 = WeightedRandomSampler(가중치, num_samples=len(학습), replacement=True,
                                  generator=torch.Generator().manual_seed(씨앗))
    print("학습용 클래스별 개수:", torch.bincount(정답).tolist())

    학습_로더 = DataLoader(학습, batch_size=32, sampler=샘플러, num_workers=2)
    검증_로더 = DataLoader(검증, batch_size=64, shuffle=False, num_workers=2)
    return 학습_로더, 검증_로더, 학습.dataset.classes


def main() -> None:
    torch.manual_seed(씨앗)
    도형_폴더_만들기(뿌리, {"circle": 120, "square": 60, "triangle": 20}, 씨앗=1)
    학습_로더, 검증_로더, 클래스들 = 로더_만들기()
    print("클래스:", 클래스들, "| 배치 수:", len(학습_로더), len(검증_로더))

    에폭_개수 = torch.zeros(len(클래스들), dtype=torch.long)
    for 단계, (그림, 정답) in enumerate(학습_로더):
        에폭_개수 += torch.bincount(정답, minlength=len(클래스들))
        if 단계 == 0:
            print("첫 배치:", tuple(그림.shape), 그림.dtype, 정답.dtype)
            print(f"첫 배치 평균 {그림.mean():.3f}, 표준편차 {그림.std():.3f}")
    print("한 에폭 동안 본 클래스별 개수:", 에폭_개수.tolist())

    첫번째 = torch.cat([그림 for 그림, _ in 검증_로더])
    두번째 = torch.cat([그림 for 그림, _ in 검증_로더])
    print("검증 데이터:", tuple(첫번째.shape), "| 두 번 읽어도 같은가:", torch.equal(첫번째, 두번째))


if __name__ == "__main__":
    main()
