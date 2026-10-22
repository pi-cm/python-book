# [2권 Chapter 18. 실험 관리와 재현성 · 18.3 체크포인트와 재개 · manuscript-vol2/chapters/18-experiment-management.md:496]
import os
import random
from pathlib import Path

import numpy as np
import torch
from torch.optim.lr_scheduler import CosineAnnealingLR

from 실험도구 import 로더_만들기, 모델_만들기, 씨앗_고정, 옷_데이터, 평가, 학습설정, 한_에폭_학습

설정 = 학습설정(드롭아웃=0.2, 에폭=4, 학습_개수=10_000)
(X_학습, y_학습), (X_검증, y_검증), _ = 옷_데이터(설정.학습_개수)


def 난수_상태() -> dict:
    """세 난수 발생기의 지금 상태. NumPy 상태는 weights_only로 읽을 수 있게 리스트로."""
    _, 표, 위치, 가우스, 남은값 = np.random.get_state()
    return {"torch": torch.get_rng_state(), "numpy": (표.tolist(), 위치, 가우스, 남은값),
            "random": random.getstate()}


def 난수_되돌리기(상태: dict) -> None:
    torch.set_rng_state(상태["torch"])
    표, 위치, 가우스, 남은값 = 상태["numpy"]
    np.random.set_state(("MT19937", np.array(표, dtype=np.uint32), 위치, 가우스, 남은값))
    random.setstate(상태["random"])


def 안전하게_저장(내용: dict, 파일: Path) -> None:
    """임시 파일에 다 쓴 다음 이름을 바꾼다. 쓰다가 꺼져도 예전 파일은 멀쩡하다."""
    임시 = 파일.with_suffix(".tmp")
    torch.save(내용, 임시)
    os.replace(임시, 파일)


def 학습(폴더: Path, 멈출_에폭: int | None = None) -> torch.nn.Module:
    """폴더에 마지막 체크포인트가 있으면 거기서부터 이어서 학습한다."""
    씨앗_고정(설정.씨앗)
    모델 = 모델_만들기(설정)
    옵티마이저 = torch.optim.Adam(모델.parameters(), lr=설정.학습률)
    스케줄러 = CosineAnnealingLR(옵티마이저, T_max=설정.에폭)
    로더 = 로더_만들기(X_학습, y_학습, 설정.배치_크기, 설정.씨앗)
    시작, 최고 = 1, 0.0
    마지막 = 폴더 / "last.pt"
    if 마지막.exists():
        상자 = torch.load(마지막, weights_only=True)
        모델.load_state_dict(상자["모델"])
        옵티마이저.load_state_dict(상자["옵티마이저"])
        스케줄러.load_state_dict(상자["스케줄러"])
        로더.generator.set_state(상자["섞기_생성기"])
        난수_되돌리기(상자["난수"])
        시작, 최고 = 상자["에폭"] + 1, 상자["최고_정확도"]
        print(f"  {상자['에폭']}에폭 체크포인트에서 이어 갑니다")
    for 에폭 in range(시작, 설정.에폭 + 1):
        한_에폭_학습(모델, 로더, 옵티마이저)
        스케줄러.step()
        if 에폭 == 멈출_에폭:
            raise RuntimeError(f"{에폭}에폭 도중 정전!")
        정확도 = 평가(모델, X_검증, y_검증)[1]
        if 정확도 > 최고:
            최고 = 정확도
            안전하게_저장({"모델": 모델.state_dict(), "에폭": 에폭, "정확도": 정확도}, 폴더 / "best.pt")
        안전하게_저장({"에폭": 에폭, "모델": 모델.state_dict(), "옵티마이저": 옵티마이저.state_dict(),
                     "스케줄러": 스케줄러.state_dict(), "섞기_생성기": 로더.generator.get_state(),
                     "난수": 난수_상태(), "최고_정확도": 최고}, 마지막)
        print(f"  에폭 {에폭}: 검증 정확도 {정확도:.2%}, 학습률 {스케줄러.get_last_lr()[0]:.6f}")
    return 모델


for 이름 in ("한번에", "이어서"):
    Path(이름).mkdir(exist_ok=True)
print("[한 번에]")
한번에 = 학습(Path("한번에"))
print("[중간에 꺼졌다가 다시]")
try:
    학습(Path("이어서"), 멈출_에폭=3)
except RuntimeError as e:
    print("  오류:", e)
이어서 = 학습(Path("이어서"))
같은가 = all(torch.equal(a, b) for a, b in zip(한번에.state_dict().values(), 이어서.state_dict().values()))
print("가중치가 같은가:", 같은가)
상자 = torch.load("이어서/last.pt", weights_only=True)
print("체크포인트에 담은 것:", list(상자))
print(f"파일 크기: last.pt {os.path.getsize('이어서/last.pt') / 1024:.0f}KB, "
      f"best.pt {os.path.getsize('이어서/best.pt') / 1024:.0f}KB")
