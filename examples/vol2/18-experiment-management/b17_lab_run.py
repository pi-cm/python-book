# [2권 Chapter 18. 실험 관리와 재현성 · 18.8 실습: 작은 실험 묶음과 재현성 보고서 · manuscript-vol2/chapters/18-experiment-management.md:1284]
import hashlib
import json
import platform
from dataclasses import asdict, replace
from pathlib import Path

import torch
import yaml

import 실험도구
from 실험도구 import 로더_만들기, 모델_만들기, 씨앗_고정, 옷_데이터, 평가, 학습설정, 한_에폭_학습

실험묶음 = yaml.safe_load("""
기준: {모델: cnn, 에폭: 4, 학습_개수: 10000}
씨앗들: [0, 1, 2]
실험들:
  6장 MLP: {모델: mlp}
  9장 CNN: {}
  CNN + 드롭아웃 0.3: {드롭아웃: 0.3}
  CNN + 학습률 0.003: {학습률: 0.003}
""")


def 지문(글: str | bytes) -> str:
    return hashlib.sha256(글 if isinstance(글, bytes) else 글.encode()).hexdigest()[:12]


def 실험_하나(이름: str, 설정: 학습설정, 데이터, 뿌리: Path = Path("runs/실습")) -> None:
    """실험 폴더 하나에 설정·환경·에폭별 기록·최고 모델·결과를 남긴다. 이미 끝났으면 건너뛴다."""
    폴더 = 뿌리 / f"{설정.모델}_{지문(json.dumps(asdict(설정), sort_keys=True))}"
    if (폴더 / "결과.json").exists():
        return
    폴더.mkdir(parents=True, exist_ok=True)
    (X_학습, y_학습), (X_검증, y_검증), _ = 데이터
    (폴더 / "설정.yaml").write_text(yaml.safe_dump({"이름": 이름, **asdict(설정)}, allow_unicode=True,
                                                   sort_keys=False), encoding="utf-8")
    환경 = {"파이썬": platform.python_version(), "torch": torch.__version__, "장치": "cpu",
            "코드_지문": 지문(Path(실험도구.__file__).read_bytes() + Path(__file__).read_bytes()),
            "데이터_지문": 지문(X_학습.numpy().tobytes() + y_학습.numpy().tobytes())}
    (폴더 / "환경.json").write_text(json.dumps(환경, ensure_ascii=False, indent=1), encoding="utf-8")

    씨앗_고정(설정.씨앗)
    모델 = 모델_만들기(설정)
    옵티마이저 = torch.optim.AdamW(모델.parameters(), lr=설정.학습률, weight_decay=설정.가중치_감쇠)
    로더 = 로더_만들기(X_학습, y_학습, 설정.배치_크기, 설정.씨앗)
    최고 = {"검증_정확도": 0.0}
    with (폴더 / "기록.jsonl").open("w", encoding="utf-8") as 기록:
        for 에폭 in range(1, 설정.에폭 + 1):
            학습_손실 = 한_에폭_학습(모델, 로더, 옵티마이저)
            검증_손실, 검증_정확도 = 평가(모델, X_검증, y_검증)
            기록.write(json.dumps({"에폭": 에폭, "학습_손실": 학습_손실, "검증_손실": 검증_손실,
                                   "검증_정확도": 검증_정확도}) + "\n")
            if 검증_정확도 > 최고["검증_정확도"]:
                최고 = {"검증_정확도": 검증_정확도, "에폭": 에폭}
                torch.save(모델.state_dict(), 폴더 / "best.pt")
    (폴더 / "결과.json").write_text(json.dumps(최고, ensure_ascii=False), encoding="utf-8")


데이터 = 옷_데이터(학습_개수=실험묶음["기준"]["학습_개수"])
기준 = 학습설정(**실험묶음["기준"])
for 이름, 바꿀값 in 실험묶음["실험들"].items():
    for 씨앗 in 실험묶음["씨앗들"]:
        실험_하나(이름, replace(기준, **바꿀값, 씨앗=씨앗), 데이터)
    print(f"[완료] {이름}")
폴더들 = sorted(p for p in Path("runs/실습").iterdir() if p.is_dir())
print(f"실험 폴더 {len(폴더들)}개, 예: {폴더들[0].name} →", sorted(p.name for p in 폴더들[0].iterdir()))
