# [2권 Chapter 12. 어텐션과 트랜스포머: 처음부터 직접 구현 · 12.8 작은 GPT 만들기 · manuscript-vol2/chapters/12-transformer.md:1032]
"""12장의 작은 문자 단위 GPT: 모델과 학습 함수."""
import math
from dataclasses import dataclass

import torch
from torch import nn
from torch.nn import functional as F

from 법전 import 데이터_폴더, 배치_뽑기, 준비, 글자표


@dataclass
class 설정:
    어휘_크기: int
    문맥_길이: int = 128       # 한 번에 보는 글자 수
    차원: int = 128            # 글자 하나를 나타내는 숫자 개수
    헤드_수: int = 4
    층_수: int = 4
    드롭아웃: float = 0.1
    위치_사용: bool = True     # 실습용 스위치: 위치 임베딩을 더할까
    인과_마스크: bool = True   # 실습용 스위치: 앞으로 올 글자를 가릴까


class 멀티헤드_어텐션(nn.Module):
    def __init__(self, s: 설정) -> None:
        super().__init__()
        self.헤드_수, self.인과_마스크 = s.헤드_수, s.인과_마스크
        self.qkv = nn.Linear(s.차원, 3 * s.차원)        # 쿼리·키·값을 한 번에
        self.출력 = nn.Linear(s.차원, s.차원)
        self.드롭아웃 = nn.Dropout(s.드롭아웃)
        self.가중치 = None                              # 들여다보기용으로 남겨 두는 어텐션 가중치

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, T, C = x.shape
        q, k, v = self.qkv(x).split(C, dim=2)
        # (B, T, C) → (B, 헤드, T, 헤드 차원)
        q, k, v = (t.view(B, T, self.헤드_수, -1).transpose(1, 2) for t in (q, k, v))
        점수 = q @ k.transpose(-2, -1) / math.sqrt(k.size(-1))     # (B, 헤드, T, T)
        if self.인과_마스크:
            미래 = torch.ones(T, T, dtype=torch.bool, device=x.device).triu(1)
            점수 = 점수.masked_fill(미래, float("-inf"))
        가중치 = 점수.softmax(dim=-1)
        self.가중치 = 가중치.detach()
        y = self.드롭아웃(가중치) @ v                              # (B, 헤드, T, 헤드 차원)
        y = y.transpose(1, 2).contiguous().view(B, T, C)          # 헤드를 다시 이어 붙이기
        return self.출력(y)


class 블록(nn.Module):
    """트랜스포머 블록: (층 정규화 → 어텐션) + 잔차, (층 정규화 → 피드포워드) + 잔차."""

    def __init__(self, s: 설정) -> None:
        super().__init__()
        self.정규화1 = nn.LayerNorm(s.차원)
        self.어텐션 = 멀티헤드_어텐션(s)
        self.정규화2 = nn.LayerNorm(s.차원)
        self.피드포워드 = nn.Sequential(
            nn.Linear(s.차원, 4 * s.차원), nn.GELU(),
            nn.Linear(4 * s.차원, s.차원), nn.Dropout(s.드롭아웃))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.어텐션(self.정규화1(x))        # 글자끼리 정보 주고받기
        x = x + self.피드포워드(self.정규화2(x))    # 글자마다 혼자 생각하기
        return x


class 작은GPT(nn.Module):
    def __init__(self, s: 설정) -> None:
        super().__init__()
        self.s = s
        self.글자_임베딩 = nn.Embedding(s.어휘_크기, s.차원)
        self.위치_임베딩 = nn.Embedding(s.문맥_길이, s.차원)
        self.드롭아웃 = nn.Dropout(s.드롭아웃)
        self.블록들 = nn.Sequential(*[블록(s) for _ in range(s.층_수)])
        self.마지막_정규화 = nn.LayerNorm(s.차원)
        self.머리 = nn.Linear(s.차원, s.어휘_크기)       # 다음 글자의 점수(로짓)

    def forward(self, 번호들: torch.Tensor) -> torch.Tensor:
        B, T = 번호들.shape
        x = self.글자_임베딩(번호들)                               # (B, T, C)
        if self.s.위치_사용:
            x = x + self.위치_임베딩(torch.arange(T, device=번호들.device))
        x = self.블록들(self.드롭아웃(x))
        return self.머리(self.마지막_정규화(x))                    # (B, T, 어휘 크기)

    @torch.no_grad()
    def 생성(self, 번호들: torch.Tensor, 개수: int) -> torch.Tensor:
        """마지막 자리의 예측 확률대로 한 글자를 뽑아 붙이기를 개수만큼 되풀이한다."""
        for _ in range(개수):
            로짓 = self(번호들[:, -self.s.문맥_길이:])[:, -1, :]      # (B, 어휘 크기)
            다음 = torch.multinomial(로짓.softmax(dim=-1), num_samples=1)
            번호들 = torch.cat([번호들, 다음], dim=1)
        return 번호들


def 장치_고르기() -> torch.device:
    """쓸 수 있는 가장 빠른 장치를 고른다."""
    if torch.cuda.is_available():
        return torch.device("cuda")       # NVIDIA GPU
    if torch.backends.mps.is_available():
        return torch.device("mps")        # Apple 실리콘 GPU
    return torch.device("cpu")


@torch.no_grad()
def 손실_재기(모델: 작은GPT, 데이터: torch.Tensor, 장치: torch.device) -> float:
    """늘 같은 자리 640곳(20배치 × 32)에서 잰 평균 손실."""
    모델.eval()
    생성기 = torch.Generator().manual_seed(0)
    합 = 0.0
    for _ in range(20):
        x, y = 배치_뽑기(데이터, 모델.s.문맥_길이, 32, 생성기)
        합 += F.cross_entropy(모델(x.to(장치)).flatten(0, 1), y.to(장치).flatten()).item()
    모델.train()
    return 합 / 20


def 학습(s: 설정, 학습_데이터: torch.Tensor, 검증_데이터: torch.Tensor,
         단계_수: int, 장치: torch.device, 보고_간격: int = 500) -> 작은GPT:
    torch.manual_seed(0)
    모델 = 작은GPT(s).to(장치)
    옵티마이저 = torch.optim.AdamW(모델.parameters(), lr=1e-3, weight_decay=0.1)
    스케줄러 = torch.optim.lr_scheduler.CosineAnnealingLR(옵티마이저, T_max=단계_수)
    생성기 = torch.Generator().manual_seed(0)
    for 단계 in range(1, 단계_수 + 1):
        x, y = 배치_뽑기(학습_데이터, s.문맥_길이, 32, 생성기)
        로짓 = 모델(x.to(장치))                                   # (32, 문맥_길이, 어휘 크기)
        손실 = F.cross_entropy(로짓.flatten(0, 1), y.to(장치).flatten())
        옵티마이저.zero_grad()
        손실.backward()
        nn.utils.clip_grad_norm_(모델.parameters(), 1.0)
        옵티마이저.step()
        스케줄러.step()
        if 단계 % 보고_간격 == 0:
            print(f"{단계:5d}단계  학습 손실 {손실_재기(모델, 학습_데이터, 장치):.3f}"
                  f"  검증 손실 {손실_재기(모델, 검증_데이터, 장치):.3f}")
    return 모델.cpu().eval()


def 학습된_모델(단계_수: int = 3000) -> tuple[작은GPT, 글자표]:
    """저장해 둔 모델이 있으면 불러오고, 없으면 학습해서 data/작은GPT.pt에 저장한다."""
    표, 학습_데이터, 검증_데이터 = 준비()
    s = 설정(어휘_크기=len(표))
    경로 = 데이터_폴더 / "작은GPT.pt"
    if 경로.exists():
        모델 = 작은GPT(s)
        모델.load_state_dict(torch.load(경로, weights_only=True))
        return 모델.eval(), 표
    모델 = 학습(s, 학습_데이터, 검증_데이터, 단계_수, 장치_고르기())
    torch.save(모델.state_dict(), 경로)
    return 모델, 표
