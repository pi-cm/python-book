import json
import statistics
from collections import defaultdict
from pathlib import Path

import torch
import yaml

from 실험도구 import 모델_만들기, 옷_데이터, 평가, 학습설정

# 1) 실험 폴더를 모두 읽어 이름별로 묶는다
묶음 = defaultdict(list)
for 폴더 in sorted(p for p in Path("runs/실습").iterdir() if p.is_dir()):
    설정값 = yaml.safe_load((폴더 / "설정.yaml").read_text(encoding="utf-8"))
    결과 = json.loads((폴더 / "결과.json").read_text(encoding="utf-8"))
    환경 = json.loads((폴더 / "환경.json").read_text(encoding="utf-8"))
    묶음[설정값.pop("이름")].append({"설정": 설정값, "결과": 결과, "환경": 환경, "폴더": 폴더})

# 2) 이름마다 씨앗 순으로 정렬해 평균과 표준편차를 내고, 검증 정확도 순으로
정확도 = {}
for 이름, 실행들 in 묶음.items():
    실행들.sort(key=lambda r: r["설정"]["씨앗"])
    정확도[이름] = [r["결과"]["검증_정확도"] * 100 for r in 실행들]
순서 = sorted(정확도, key=lambda 이름: statistics.mean(정확도[이름]), reverse=True)

보고서 = ["# 재현성 보고서: FashionMNIST 작은 실험 묶음", "",
          "| 실험 | 씨앗 0, 1, 2의 검증 정확도(%) | 평균 ± 표준편차 | 9장 CNN과 같은 씨앗끼리 차이(%p) |",
          "|---|---|---|---|"]
for 이름 in 순서:
    값들 = 정확도[이름]
    차이 = [a - b for a, b in zip(값들, 정확도["9장 CNN"])]
    보고서.append(f"| {이름} | {', '.join(f'{v:.2f}' for v in 값들)} | "
                  f"{statistics.mean(값들):.2f} ± {statistics.stdev(값들):.2f} | "
                  f"{', '.join(f'{d:+.2f}' for d in 차이)} |")

# 3) 검증으로 고른 실험 하나만, 시험 데이터로 마지막에 한 번
고른_이름 = 순서[0]
실행들 = 묶음[고른_이름]
_, _, (X_시험, y_시험) = 옷_데이터()
시험 = []
for r in 실행들:
    모델 = 모델_만들기(학습설정(**r["설정"]))
    모델.load_state_dict(torch.load(r["폴더"] / "best.pt", weights_only=True))
    시험.append(평가(모델, X_시험, y_시험)[1] * 100)
환경 = 실행들[0]["환경"]
같은_환경 = all(r["환경"] == 환경 for 실행 in 묶음.values() for r in 실행)
보고서 += ["", f"- 고른 실험: {고른_이름} (검증 평균이 가장 높음)",
           f"- 시험 정확도: {statistics.mean(시험):.2f} ± {statistics.stdev(시험):.2f}% (씨앗 {len(시험)}개)",
           f"- 공통 설정: {json.dumps({k: v for k, v in 실행들[0]['설정'].items() if k != '씨앗'}, ensure_ascii=False)}",
           f"- 환경: 파이썬 {환경['파이썬']}, PyTorch {환경['torch']}, 장치 {환경['장치']}",
           f"- 코드 지문 {환경['코드_지문']}, 데이터 지문 {환경['데이터_지문']}, 모든 실험이 같은 환경: {같은_환경}"]
Path("runs/실습/보고서.md").write_text("\n".join(보고서) + "\n", encoding="utf-8")
print("\n".join(보고서))
