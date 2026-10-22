# [2권 Chapter 13. 한국어 NLP 실전: 토크나이저부터 감성 분류까지 · 13.1 이 장의 데이터: 네이버 영화 리뷰 · manuscript-vol2/chapters/13-korean-nlp.md:56]
"""13장 예제들이 함께 쓰는 NSMC(네이버 영화 리뷰) 받기·읽기 도구."""
import csv
import random
import urllib.request
from pathlib import Path

# 원본 저장소: github.com/e9t/nsmc (CC0 1.0, 퍼블릭 도메인)
주소 = "https://raw.githubusercontent.com/e9t/nsmc/master/"
폴더 = Path("data/nsmc")


def NSMC_받기() -> None:
    """학습·시험 파일이 없으면 내려받는다(합쳐서 약 19MB)."""
    폴더.mkdir(parents=True, exist_ok=True)
    for 파일 in ["ratings_train.txt", "ratings_test.txt"]:
        if not (폴더 / 파일).exists():
            urllib.request.urlretrieve(주소 + 파일, 폴더 / 파일)


def NSMC_읽기(파일: str, 개수: int | None = None, 씨앗: int = 0) -> list[tuple[str, int]]:
    """(문장, 라벨) 목록을 돌려준다. 빈 문장은 버리고, 개수를 주면 무작위로 그만큼 고른다."""
    NSMC_받기()
    with open(폴더 / 파일, encoding="utf-8", newline="") as f:
        줄들 = list(csv.reader(f, delimiter="\t"))[1:]       # 첫 줄은 열 이름
    자료 = [(문장.strip(), int(라벨)) for _, 문장, 라벨 in 줄들 if 문장.strip()]
    if 개수 is not None:
        자료 = random.Random(씨앗).sample(자료, 개수)
    return 자료
