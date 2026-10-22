# [2권 Chapter 8. 학습 잘 시키기 · 8.12 실습: 외우는 신경망에 대책을 하나씩 더하기 · manuscript-vol2/chapters/08-training-well.md:1330]
import copy

import torch
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader, Dataset
from torchvision.transforms import v2

from 학습도구 import 데이터_준비, 로더_만들기, 모델_만들기, 평가, 한_에폭_학습

(X_학습, y_학습), (X_검증, y_검증), (X_테스트, y_테스트) = 데이터_준비()
최대_에폭 = 150


class 이동_데이터셋(Dataset):
    """꺼낼 때마다 8×8 숫자를 위아래·좌우로 최대 한 칸씩 무작위로 옮긴다(7장의 RandomCrop)."""

    def __init__(self, X: torch.Tensor, y: torch.Tensor) -> None:
        self.X, self.y = X.reshape(-1, 1, 8, 8), y
        self.옮기기 = v2.RandomCrop(size=8, padding=1)    # 0으로 한 칸 두른 뒤 8×8로 자르기

    def __len__(self) -> int:
        return len(self.y)

    def __getitem__(self, i: int) -> tuple[torch.Tensor, torch.Tensor]:
        return self.옮기기(self.X[i]).flatten(), self.y[i]


def 실험(씨앗: int, wd: float = 0.0, 드롭아웃: float = 0.0, 배치정규화: bool = False,
         조기종료: bool = False, 코사인: bool = False, 증강: bool = False) -> tuple[dict, torch.nn.Module]:
    """설정 하나로 학습하고 결과 수치와 모델을 돌려준다."""
    torch.manual_seed(씨앗)
    로더 = 로더_만들기(X_학습, y_학습)
    if 증강:                                   # 학습 데이터에만 증강
        로더 = DataLoader(이동_데이터셋(X_학습, y_학습), batch_size=32, shuffle=True,
                          generator=torch.Generator().manual_seed(0))
    모델 = 모델_만들기(드롭아웃=드롭아웃, 배치정규화=배치정규화)
    옵티마이저 = torch.optim.AdamW(모델.parameters(), lr=1e-3, weight_decay=wd)
    스케줄러 = CosineAnnealingLR(옵티마이저, T_max=최대_에폭) if 코사인 else None
    최고_손실, 최고_가중치, 참은_횟수, 멈춘_에폭 = float("inf"), None, 0, 최대_에폭
    for 에폭 in range(1, 최대_에폭 + 1):
        한_에폭_학습(모델, 로더, 옵티마이저)
        if 스케줄러:
            스케줄러.step()
        검증_손실, _ = 평가(모델, X_검증, y_검증)
        if 검증_손실 < 최고_손실:
            최고_손실, 최고_가중치, 참은_횟수 = 검증_손실, copy.deepcopy(모델.state_dict()), 0
        else:
            참은_횟수 += 1
        if 조기종료 and 참은_횟수 >= 20:
            멈춘_에폭 = 에폭
            break
    if 조기종료:
        모델.load_state_dict(최고_가중치)     # 가장 좋았던 순간으로
    _, 학습_정확도 = 평가(모델, X_학습, y_학습)
    검증_손실, 검증_정확도 = 평가(모델, X_검증, y_검증)
    return dict(학습=학습_정확도, 손실=검증_손실, 검증=검증_정확도, 에폭=멈춘_에폭), 모델


단계들 = [
    ("1. 기준 (대책 없음)", {}),
    ("2. + weight decay 1.0", dict(wd=1.0)),
    ("3. + 드롭아웃 0.5", dict(wd=1.0, 드롭아웃=0.5)),
    ("4. + 배치 정규화", dict(wd=1.0, 드롭아웃=0.5, 배치정규화=True)),
    ("5. 3번 + 조기 종료", dict(wd=1.0, 드롭아웃=0.5, 조기종료=True)),
    ("6. 5번 + 코사인 스케줄러", dict(wd=1.0, 드롭아웃=0.5, 조기종료=True, 코사인=True)),
    ("7. 5번 + 데이터 증강", dict(wd=1.0, 드롭아웃=0.5, 조기종료=True, 증강=True)),
    ("8. 기준 + 데이터 증강만", dict(증강=True)),
]
씨앗들 = [0, 1, 2]
print("학습정확도  검증손실  검증정확도  멈춘에폭  단계")
for 이름, 설정 in 단계들:
    결과들 = [실험(씨앗, **설정)[0] for 씨앗 in 씨앗들]
    평균 = {k: sum(r[k] for r in 결과들) / len(결과들) for k in 결과들[0]}
    print(f"{평균['학습']:9.1%}  {평균['손실']:8.3f}  {평균['검증']:9.1%}  {평균['에폭']:8.0f}  {이름}")

# 검증 성적으로 고른 5번을, 한 번도 쓰지 않은 테스트 데이터로 마지막에 확인
for 이름, 설정 in [단계들[0], 단계들[4]]:
    정확도들 = [평가(실험(씨앗, **설정)[1], X_테스트, y_테스트)[1] for 씨앗 in 씨앗들]
    print(f"테스트 정확도 {sum(정확도들) / len(정확도들):.1%}  <- {이름}")
