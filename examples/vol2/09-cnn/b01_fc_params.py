# [2권 Chapter 9. CNN과 이미지 분류: 돋보기를 옮기며 무늬 찾기 · 들어가며: 사진을 한 줄로 펴면 무엇을 잃을까요? · manuscript-vol2/chapters/09-cnn.md:24]
from torch import nn


def 파라미터_수(층: nn.Module) -> int:
    """층 하나에 들어 있는 학습할 숫자의 개수."""
    return sum(p.numel() for p in 층.parameters())


# (색 채널, 세로, 가로)
사진들 = {"FashionMNIST 옷 사진": (1, 28, 28), "작게 줄인 컬러 사진": (3, 224, 224)}
for 이름, (채널, 세로, 가로) in 사진들.items():
    완전연결 = nn.Linear(채널 * 세로 * 가로, 256)            # 한 줄로 펴서 256칸에 모두 연결
    합성곱 = nn.Conv2d(채널, 256, kernel_size=3)             # 3×3 돋보기 256개 (9.1절)
    print(f"{이름} {채널}×{세로}×{가로}")
    print(f"  완전 연결층: {파라미터_수(완전연결):>12,}개 ({파라미터_수(완전연결) * 4 / 1024**2:7.2f} MB)")
    print(f"  합성곱층   : {파라미터_수(합성곱):>12,}개 ({파라미터_수(합성곱) * 4 / 1024**2:7.2f} MB)")
