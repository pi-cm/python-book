# [2권 Chapter 18. 실험 관리와 재현성 · 18.4 실험 기록 남기기 · manuscript-vol2/chapters/18-experiment-management.md:628]
import json
from pathlib import Path

import torch

from 실험도구 import 로더_만들기, 모델_만들기, 씨앗_고정, 옷_데이터, 평가, 학습설정, 한_에폭_학습


class 기록장:
    """에폭마다 한 줄씩 JSON으로 덧붙여 쓰는 기록 파일 (JSON Lines)."""

    def __init__(self, 파일: Path) -> None:
        파일.parent.mkdir(parents=True, exist_ok=True)
        self.파일 = 파일.open("a", encoding="utf-8")

    def 적기(self, **값) -> None:
        self.파일.write(json.dumps(값, ensure_ascii=False) + "\n")
        self.파일.flush()                  # 학습이 중간에 죽어도 여기까지는 남는다

    def __enter__(self) -> "기록장":
        return self

    def __exit__(self, *오류) -> None:
        self.파일.close()


설정 = 학습설정(에폭=4, 학습_개수=10_000)
(X_학습, y_학습), (X_검증, y_검증), _ = 옷_데이터(설정.학습_개수)
씨앗_고정(설정.씨앗)
모델 = 모델_만들기(설정)
옵티마이저 = torch.optim.Adam(모델.parameters(), lr=설정.학습률)
로더 = 로더_만들기(X_학습, y_학습, 설정.배치_크기, 설정.씨앗)

with 기록장(Path("runs/기록연습/기록.jsonl")) as 기록:
    for 에폭 in range(1, 설정.에폭 + 1):
        학습_손실 = 한_에폭_학습(모델, 로더, 옵티마이저)
        검증_손실, 검증_정확도 = 평가(모델, X_검증, y_검증)
        기록.적기(에폭=에폭, 학습_손실=round(학습_손실, 4), 검증_손실=round(검증_손실, 4),
                 검증_정확도=round(검증_정확도, 4))

줄들 = Path("runs/기록연습/기록.jsonl").read_text(encoding="utf-8").splitlines()
print(줄들[0])
기록들 = [json.loads(줄) for 줄 in 줄들]
최고 = max(기록들, key=lambda r: r["검증_정확도"])
print(f"{len(기록들)}줄 기록, 가장 좋았던 에폭 {최고['에폭']}: {최고['검증_정확도']:.2%}")
