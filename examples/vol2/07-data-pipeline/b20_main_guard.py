# [2권 Chapter 7. 데이터 파이프라인: Dataset과 DataLoader · 7.10 num_workers와 병목 찾기 · manuscript-vol2/chapters/07-data-pipeline.md:1077]
import subprocess
import sys
from pathlib import Path

가드_없음 = """
import torch
from torch.utils.data import DataLoader, TensorDataset

로더 = DataLoader(TensorDataset(torch.arange(8)), batch_size=4, num_workers=2)
for (배치,) in 로더:
    print("배치:", 배치.tolist())
"""

가드_있음 = """
import torch
from torch.utils.data import DataLoader, TensorDataset


def main() -> None:
    로더 = DataLoader(TensorDataset(torch.arange(8)), batch_size=4, num_workers=2)
    for (배치,) in 로더:
        print("배치:", 배치.tolist())


if __name__ == "__main__":
    main()
"""

for 이름, 본문 in [("가드_없음.py", 가드_없음), ("가드_있음.py", 가드_있음)]:
    Path(이름).write_text(본문, encoding="utf-8")            # 파일로 저장해서
    결과 = subprocess.run([sys.executable, 이름],              # 따로 실행해 본다
                          capture_output=True, text=True, timeout=120)
    print(f"--- {이름} (종료 코드 {결과.returncode})")
    if 결과.stdout:
        print(결과.stdout.strip())
    줄들 = [줄.strip() for 줄 in 결과.stderr.splitlines()]
    첫줄 = "An attempt has been made to start a new process before the"
    if 첫줄 in 줄들:                                          # 일꾼 프로세스가 남긴 설명
        시작 = 줄들.index(첫줄)
        print("\n".join(줄들[시작:시작 + 6]))
