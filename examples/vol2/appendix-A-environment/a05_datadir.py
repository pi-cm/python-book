# [2권 부록 A. 실행 환경 만들기 · A.9 데이터 폴더 관례: BOOK_DATA_DIR · manuscript-vol2/appendix/A-environment.md:472]
import os
from pathlib import Path


def 데이터_폴더() -> Path:
    """예제 데이터를 둘 폴더. BOOK_DATA_DIR이 있으면 그곳, 없으면 ./data"""
    return Path(os.environ.get("BOOK_DATA_DIR", "data"))


os.environ.pop("BOOK_DATA_DIR", None)            # 지정하지 않았을 때
print(데이터_폴더())
os.environ["BOOK_DATA_DIR"] = "/Volumes/외장/책데이터"  # 지정했을 때 (예)
print(데이터_폴더())
print(데이터_폴더() / "FashionMNIST")
