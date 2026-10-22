# [2권 Chapter 7. 데이터 파이프라인: Dataset과 DataLoader · 7.5 직접 만든 Dataset ②: 이미지 폴더 · manuscript-vol2/chapters/07-data-pipeline.md:437]
# 도형_만들기.py — 예제용 도형 그림 폴더를 만드는 모듈
import random
from pathlib import Path

from PIL import Image, ImageDraw


def 도형_그리기(모양: str, rng: random.Random) -> Image.Image:
    """흰 바탕 32×32 그림에 무작위 색·크기·위치로 도형 하나를 그린다."""
    그림 = Image.new("RGB", (32, 32), "white")
    펜 = ImageDraw.Draw(그림)
    크기 = rng.randint(12, 22)
    x, y = rng.randint(1, 31 - 크기), rng.randint(1, 31 - 크기)
    색 = tuple(rng.randint(0, 200) for _ in range(3))
    if 모양 == "circle":
        펜.ellipse([x, y, x + 크기, y + 크기], fill=색)
    elif 모양 == "square":
        펜.rectangle([x, y, x + 크기, y + 크기], fill=색)
    else:
        펜.polygon([(x + 크기 // 2, y), (x, y + 크기), (x + 크기, y + 크기)], fill=색)
    return 그림


def 도형_폴더_만들기(뿌리: Path, 개수: dict[str, int], 씨앗: int = 0) -> None:
    """뿌리/모양/번호.png 구조로 그림을 저장한다. 폴더가 이미 있으면 건너뛴다."""
    if 뿌리.exists():
        return
    rng = random.Random(씨앗)
    for 모양, n in 개수.items():
        폴더 = 뿌리 / 모양                      # 폴더 이름이 곧 정답(클래스)
        폴더.mkdir(parents=True)
        for i in range(n):
            도형_그리기(모양, rng).save(폴더 / f"{i:03d}.png")


if __name__ == "__main__":
    뿌리 = Path("data/shapes")
    도형_폴더_만들기(뿌리, {"circle": 20, "square": 20, "triangle": 20})
    for 폴더 in sorted(뿌리.iterdir()):
        파일들 = sorted(폴더.glob("*.png"))
        print(f"{폴더.name}: {len(파일들)}개", [f.name for f in 파일들[:3]], "...")
