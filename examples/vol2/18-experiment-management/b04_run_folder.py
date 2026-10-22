# [2권 Chapter 18. 실험 관리와 재현성 · 18.2 설정을 코드 밖으로 · manuscript-vol2/chapters/18-experiment-management.md:356]
import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path

import yaml

from 실험도구 import 학습설정


def 설정_지문(설정: 학습설정) -> str:
    """설정의 모든 값을 정해진 순서로 글자로 만든 뒤 해시한 앞 8글자."""
    글 = json.dumps(asdict(설정), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(글.encode("utf-8")).hexdigest()[:8]


def 실험_폴더(설정: 학습설정, 뿌리: Path = Path("runs")) -> Path | None:
    """설정마다 폴더를 하나 만들고 설정을 적어 둔다. 이미 있으면 None."""
    폴더 = 뿌리 / f"{설정.모델}_lr{설정.학습률:g}_s{설정.씨앗}_{설정_지문(설정)}"
    if 폴더.exists():
        return None                                   # 같은 실험을 두 번 하지 않는다
    폴더.mkdir(parents=True)
    (폴더 / "설정.yaml").write_text(yaml.safe_dump(asdict(설정), allow_unicode=True, sort_keys=False),
                                   encoding="utf-8")
    return 폴더


기준 = 학습설정()
print("기준 지문     :", 설정_지문(기준))
print("다시 만들어도 :", 설정_지문(학습설정()))
print("씨앗만 바꿔도 :", 설정_지문(replace(기준, 씨앗=1)))

for 설정 in [기준, replace(기준, 학습률=3e-3), 기준]:
    폴더 = 실험_폴더(설정)
    if 폴더 is None:
        print("이미 한 실험이라 건너뜀")
    else:
        print("새 폴더:", 폴더)

print((Path("runs") / f"mlp_lr0.001_s0_{설정_지문(기준)}" / "설정.yaml").read_text(encoding="utf-8"))
