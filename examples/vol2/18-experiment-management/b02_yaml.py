# [2권 Chapter 18. 실험 관리와 재현성 · 18.2 설정을 코드 밖으로 · manuscript-vol2/chapters/18-experiment-management.md:120]
from dataclasses import dataclass, fields
from pathlib import Path

import yaml


@dataclass(frozen=True)
class 학습설정:
    모델: str = "mlp"
    학습률: float = 1e-3
    배치_크기: int = 64
    에폭: int = 2
    드롭아웃: float = 0.0
    씨앗: int = 0


Path("설정_cnn.yaml").write_text("""\
# 9장 CNN에 드롭아웃을 더한 실험
모델: cnn
학습률: 3e-4
드롭아웃: 0.3
""", encoding="utf-8")

읽은값 = yaml.safe_load(Path("설정_cnn.yaml").read_text(encoding="utf-8"))
print(읽은값)
print("학습률의 자료형:", type(읽은값["학습률"]).__name__)


def 설정_만들기(값들: dict) -> 학습설정:
    """딕셔너리를 검사해서 설정으로 바꾼다. 모르는 이름과 틀린 자료형을 잡아낸다."""
    필드 = {f.name: f.type for f in fields(학습설정)}
    모르는_이름 = set(값들) - set(필드)
    if 모르는_이름:
        raise KeyError(f"모르는 설정 이름: {sorted(모르는_이름)}")
    바꾼값 = {}
    for 이름, 값 in 값들.items():
        자료형 = 필드[이름]                   # str, float, int
        if 자료형 is float and isinstance(값, (str, int)):
            값 = float(값)                    # "3e-4" 같은 글자도 실수로
        if not isinstance(값, 자료형):
            raise TypeError(f"{이름}은(는) {자료형.__name__}이어야 하는데 {값!r}")
        바꾼값[이름] = 값
    return 학습설정(**바꾼값)


print(설정_만들기(읽은값))
for 잘못된_값 in [{"학습율": 0.01}, {"에폭": "열"}]:
    try:
        설정_만들기(잘못된_값)
    except (KeyError, TypeError) as e:
        print(type(e).__name__, e)
