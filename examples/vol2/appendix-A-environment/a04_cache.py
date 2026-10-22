# [2권 부록 A. 실행 환경 만들기 · A.8 내려받은 모델은 어디에 쌓일까: 캐시와 디스크 용량 · manuscript-vol2/appendix/A-environment.md:391]
import os
from pathlib import Path

import torch
from huggingface_hub import constants


def 짧게(경로: str | Path) -> str:
    """사용자 폴더 부분을 ~로 줄여서 보여 준다."""
    return str(경로).replace(str(Path.home()), "~")


print("HF_HOME 지정  :", os.environ.get("HF_HOME", "(지정 안 함)"))
print("Hugging Face  :", 짧게(constants.HF_HOME))
print("  모델 캐시   :", 짧게(constants.HF_HUB_CACHE))
print("torchvision   :", 짧게(torch.hub.get_dir()))
print("데이터 폴더   :", os.environ.get("BOOK_DATA_DIR", "data"))
