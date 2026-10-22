# [2권 Chapter 21. 종합 프로젝트: 맛집 추천 AI · 21.10 실험 기록과 여러 씨앗 · manuscript-vol2/chapters/21-capstone-recommender.md:1092]
import hashlib
import json
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from 맛집데이터 import 데이터_만들기, 시간으로_나누기
from 순위지표 import 평가셋_만들기, 평가하기
from 추천학습 import 내적추천, 행렬분해, 학습설정, 학습하기, 좋았던_쌍
from 투타워 import 투타워


@dataclass(frozen=True)
class 실험:
    모델: str                   # "행렬분해" 또는 "투타워"
    손실: str                   # "bce" 또는 "bpr"
    씨앗: int
    에폭: int = 60
    데이터_씨앗: int = 0


데이터 = 데이터_만들기(씨앗=0)
데이터_지문 = hashlib.sha256(pd.util.hash_pandas_object(데이터.방문).to_numpy().tobytes()).hexdigest()
학습, 검증, 시험 = 시간으로_나누기(데이터.방문)
검증셋 = 평가셋_만들기(학습, 검증, 데이터.식당)
시험셋 = 평가셋_만들기(pd.concat([학습, 검증]), 시험, 데이터.식당)
쌍, 후보_식당 = 좋았던_쌍(학습), torch.tensor(np.flatnonzero(데이터.식당["개업일"] < 300))


def 점수표(모델: 내적추천, 사용자: np.ndarray) -> np.ndarray:
    with torch.no_grad():
        return 모델.모든_점수(torch.tensor(사용자)).numpy()


def 돌리기(설정: 실험) -> dict:
    torch.manual_seed(설정.씨앗)
    모델 = (행렬분해(len(데이터.사용자), len(데이터.식당)) if 설정.모델 == "행렬분해"
          else 투타워(데이터.사용자, 데이터.식당))
    기록 = 학습하기(모델, 쌍, 후보_식당, 학습설정(손실=설정.손실, 에폭=설정.에폭, 씨앗=설정.씨앗),
                 lambda m: 평가하기(점수표(m, 검증셋.사용자), 검증셋)["NDCG@10"])
    최고 = max(기록, key=lambda 줄: 줄["검증"])
    return {"최고_에폭": 최고["에폭"], "검증_NDCG@10": 최고["검증"],
            **{f"시험_{k}": v for k, v in 평가하기(점수표(모델, 시험셋.사용자), 시험셋).items()}}


기록_파일 = Path("실험기록") / "21장_비교.jsonl"
기록_파일.parent.mkdir(exist_ok=True)
설정들 = [실험(모델, 손실, 씨앗) for 모델, 손실 in [("행렬분해", "bce"), ("행렬분해", "bpr"), ("투타워", "bpr")]
        for 씨앗 in (0, 1, 2)]
with 기록_파일.open("w", encoding="utf-8") as f:
    for 설정 in 설정들:
        글 = json.dumps(asdict(설정), ensure_ascii=False, sort_keys=True)
        줄 = {"설정_지문": hashlib.sha256(글.encode()).hexdigest()[:10], "설정": asdict(설정),
             "데이터_지문": 데이터_지문[:16], "torch": torch.__version__, **돌리기(설정)}
        f.write(json.dumps(줄, ensure_ascii=False) + "\n")
        f.flush()                                    # 중간에 끊겨도 끝난 실험은 남는다 (18장 18.4절)

결과 = pd.DataFrame([json.loads(줄) for 줄 in 기록_파일.read_text(encoding="utf-8").splitlines()])
결과["이름"] = [f"{s['모델']}·{s['손실']}" for s in 결과["설정"]]
print("기록", len(결과), "줄, 데이터 지문", 결과["데이터_지문"][0], "\n")
print("시험 NDCG@10 (씨앗 0, 1, 2)          평균 ± 표준편차  | 실험")
for 이름, 묶음 in 결과.groupby("이름", sort=False):
    값 = 묶음["시험_NDCG@10"].tolist()
    print(" ".join(f"{v:.4f}" for v in 값), f"  {statistics.mean(값):.4f} ± {statistics.stdev(값):.4f}  | {이름}")

for 상대 in ["행렬분해·bce", "투타워·bpr"]:
    차이 = (결과[결과["이름"] == 상대]["시험_NDCG@10"].to_numpy()
          - 결과[결과["이름"] == "행렬분해·bpr"]["시험_NDCG@10"].to_numpy())
    print(f"{상대} - 행렬분해·bpr (같은 씨앗끼리): {np.round(차이, 4).tolist()}")
