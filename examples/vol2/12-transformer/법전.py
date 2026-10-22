# [2권 Chapter 12. 어텐션과 트랜스포머: 처음부터 직접 구현 · 12.8 작은 GPT 만들기 · manuscript-vol2/chapters/12-transformer.md:861]
"""12장 작은 GPT의 학습 재료: 대한민국헌법과 민법 조문을 받아 글자 번호로 바꾼다."""
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

import torch

데이터_폴더 = Path(os.environ.get("BOOK_DATA_DIR", "data"))
위키문헌 = "https://ko.wikisource.org/w/index.php?action=raw&title="
# 위키문헌 문서 제목: (본문이 시작하는 제목, 끝나는 제목). 부칙은 뺀다
원문들 = {"대한민국헌법 (제10호)": ("== 전문 ==", "== 부칙 =="),
          "민법 (대한민국, 제17503호)": ("== 본칙 ==", "== 부칙 ==")}


def 위키문헌_조문(제목: str, 시작: str, 끝: str) -> list[str]:
    """위키문헌에서 법령 원문을 받아 위키 문법을 지우고 줄 목록으로 돌려준다."""
    요청 = urllib.request.Request(위키문헌 + urllib.parse.quote(제목),
                                  headers={"User-Agent": "python-book-example"})
    with urllib.request.urlopen(요청, timeout=30) as 응답:
        원문 = 응답.read().decode("utf-8")
    줄들 = []
    for 줄 in 원문.split(시작)[1].split(끝)[0].splitlines():
        if re.match(r"==[^=]", 줄):                                  # 큰 제목(조문, 본칙)은 버린다
            continue
        줄 = re.sub(r"<[^>]+>|'''|\{\{[^}]*\}\}|^[*:]+\s*", "", 줄)    # 태그, 굵게, 틀, 목록 기호
        줄 = re.sub(r"\[\[(?:[^]|]*\|)?([^]]*)\]{1,2}", r"\1", 줄)    # [[#1001|제1001조]] → 제1001조
        줄 = re.sub(r"\([\u4e00-\u9fff·]+\)", "", 줄)                # 괄호 속 한자 풀이
        줄 = re.sub(r"^=+\s*(.*?)\s*=+$", r"\1", 줄).strip()          # === 제1장 총강 === → 제1장 총강
        if 줄 and not 줄.startswith("["):                            # [본조신설 …] 같은 개정 기록
            줄들.append(줄)
    return 줄들


def 법전_읽기() -> str:
    """헌법과 민법 조문을 이어 붙인 글. 처음 한 번만 받아서 data/법전.txt에 저장한다."""
    경로 = 데이터_폴더 / "법전.txt"
    if not 경로.exists():
        줄들 = [줄 for 제목, (시작, 끝) in 원문들.items() for 줄 in 위키문헌_조문(제목, 시작, 끝)]
        데이터_폴더.mkdir(parents=True, exist_ok=True)
        경로.write_text("\n".join(줄들) + "\n", encoding="utf-8")
    return 경로.read_text(encoding="utf-8")


class 글자표:
    """글자와 번호를 서로 바꿔 주는 표."""

    def __init__(self, 글: str) -> None:
        self.글자들 = sorted(set(글))
        self.번호 = {글자: i for i, 글자 in enumerate(self.글자들)}

    def __len__(self) -> int:
        return len(self.글자들)

    def 인코딩(self, 글: str) -> torch.Tensor:
        return torch.tensor([self.번호[글자] for 글자 in 글])

    def 디코딩(self, 번호들: torch.Tensor) -> str:
        return "".join(self.글자들[i] for i in 번호들.tolist())


def 준비() -> tuple[글자표, torch.Tensor, torch.Tensor]:
    """글 전체를 번호로 바꿔 앞 90%는 학습용, 뒤 10%는 검증용으로 나눈다."""
    글 = 법전_읽기()
    표 = 글자표(글)
    전체 = 표.인코딩(글)
    경계 = int(len(전체) * 0.9)
    return 표, 전체[:경계], 전체[경계:]


def 배치_뽑기(데이터: torch.Tensor, 문맥_길이: int, 배치_크기: int,
             생성기: torch.Generator) -> tuple[torch.Tensor, torch.Tensor]:
    """아무 곳에서나 문맥_길이만큼 잘라 입력으로, 한 글자 밀린 조각을 정답으로."""
    시작 = torch.randint(len(데이터) - 문맥_길이, (배치_크기,), generator=생성기)
    x = torch.stack([데이터[i:i + 문맥_길이] for i in 시작])
    y = torch.stack([데이터[i + 1:i + 1 + 문맥_길이] for i in 시작])
    return x, y
