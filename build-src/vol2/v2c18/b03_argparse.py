import argparse
from dataclasses import asdict, dataclass, fields, replace
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


def 명령줄_해석기() -> argparse.ArgumentParser:
    """설정의 필드마다 --이름 옵션을 하나씩 만든다. 기본값은 None(=말하지 않음)."""
    해석기 = argparse.ArgumentParser(prog="학습.py", description="옷 분류 실험")
    해석기.add_argument("--설정", type=Path, help="YAML 설정 파일")
    for f in fields(학습설정):
        해석기.add_argument(f"--{f.name}", type=f.type, default=None)
    return 해석기


def 설정_읽기(명령줄: list[str]) -> 학습설정:
    """기본값 < YAML 파일 < 명령줄 순서로 덮어쓴다."""
    인자 = vars(명령줄_해석기().parse_args(명령줄))
    설정 = 학습설정()                                         # 1) 기본값
    파일 = 인자.pop("설정")
    if 파일:
        파일값 = yaml.safe_load(파일.read_text(encoding="utf-8"))
        설정 = replace(설정, **{k: type(getattr(설정, k))(v) for k, v in 파일값.items()})   # 2) 파일
    준값 = {k: v for k, v in 인자.items() if v is not None}
    return replace(설정, **준값)                              # 3) 명령줄


Path("설정_cnn.yaml").write_text("모델: cnn\n학습률: 3e-4\n드롭아웃: 0.3\n", encoding="utf-8")

print(설정_읽기([]))
print(설정_읽기(["--설정", "설정_cnn.yaml"]))
print(설정_읽기(["--설정", "설정_cnn.yaml", "--학습률", "0.001", "--씨앗", "7"]))
print(asdict(설정_읽기(["--에폭", "5"])))
명령줄_해석기().print_usage()
