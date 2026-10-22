# Chapter 18. 실험 관리와 재현성

> **학습 목표**  
> - 실험 하나를 이루는 것(설정, 코드, 데이터, 환경, 난수, 결과)을 나열하고 왜 모두 남겨야 하는지 설명하기
> - 설정을 dataclass·YAML·명령줄 인자로 코드 밖에 두고, 우선순위에 따라 덮어쓰기
> - 옵티마이저·스케줄러·난수 상태까지 담은 체크포인트로 중단된 학습을 똑같이 이어 가기
> - JSON Lines, TensorBoard, MLflow로 실험 기록을 남기고 꺼내 비교하기
> - Optuna로 하이퍼파라미터를 자동으로 탐색하고, 가망 없는 시도를 중간에 멈추기
> - 여러 씨앗으로 돌려 평균과 표준편차로 보고하고, 같은 씨앗끼리 짝지어 차이를 판단하기
> - 데이터·코드·환경의 지문을 남기고 재현성 보고서를 만들기

---

## 들어가며: 그 86%는 어떤 설정이었을까요?

석 달 전에 만든 모델이 86% 남짓을 냈다고 해 봅시다. 팀장님이 묻습니다. "그때 학습률이 얼마였죠? 드롭아웃은 넣었나요? 데이터는 지금 거랑 같은 거예요?" 폴더를 열어 보면 이런 파일들이 보입니다.

```text
model.pt
model_final.pt
model_final_v2.pt
model_final_v2_lr0.001_진짜최종.pt
train.py
train_copy.py
결과정리(수정).xlsx
```

어느 파일이 86%를 냈는지, 그때 `train.py`가 지금의 `train.py`와 같았는지 아무도 모릅니다. 요리로 치면 맛있게 끓인 찌개의 레시피를 적어 두지 않은 셈이에요. 한 번 맛있게 끓였다는 기억만 남고, 다시 끓이면 그 맛이 안 납니다.

이 책에서도 비슷한 일을 이미 겪었어요. 6장 6.11절에서 같은 모델, 같은 씨앗으로 학습했는데 한 번은 86.26%, 한 번은 86.07%가 나왔죠. 평가를 언제 했느냐에 따라 데이터를 섞는 순서가 달라졌기 때문이었습니다. 8장 8.10절에서는 씨앗을 고정하는 체크리스트를 만들었고요. 이 장은 그 체크리스트를 **실험 전체를 관리하는 습관**으로 넓힙니다.

이 장에서 할 일은 크게 세 가지입니다. 첫째, 설정·체크포인트·기록을 남겨서 **같은 실험을 다시 할 수 있게** 만듭니다. 둘째, 하이퍼파라미터 탐색과 여러 씨앗 실험을 자동으로 돌려서 **실험을 많이, 체계적으로** 합니다. 셋째, 데이터·코드·환경의 지문을 붙인 보고서로 **결과를 믿을 수 있게** 만듭니다.

> **Q. 이 장에 필요한 패키지는 무엇인가요?**
> PyTorch와 torchvision에 더해 `uv add tensorboard mlflow optuna pyyaml scikit-learn`을 실행하세요. 이 장의 예제는 파이썬 3.12, PyTorch 2.14.1, torchvision 0.29.1, TensorBoard 2.21.0, MLflow 3.17.2, Optuna 5.0.0, PyYAML 6.0.3, scikit-learn 1.9.1에서 실행해 확인했습니다. 결과를 똑같이 재현하려고 학습은 모두 CPU에서 했어요. 기록 파일과 데이터베이스는 예제를 실행한 폴더 안에 만들어집니다.

## 18.1 실험 하나를 이루는 것

정확도 86%라는 숫자 하나 뒤에는 무엇이 숨어 있을까요? 같은 숫자를 다시 얻으려면 무엇이 같아야 하는지 하나씩 꼽아 보면 이렇습니다.

| 구성 요소 | 예 | 바뀌면 생기는 일 | 이 장에서 남기는 방법 |
|---|---|---|---|
| 설정 | 학습률, 배치 크기, 에폭, 드롭아웃 | 결과가 바로 달라진다 | dataclass·YAML (18.2절) |
| 코드 | 모델 구조, 학습 루프, 전처리 | 같은 설정이어도 다른 실험이 된다 | git 커밋, 파일 지문 (18.7절) |
| 데이터 | 어떤 파일을 어떻게 나눴나 | 점수의 기준 자체가 바뀐다 | 데이터 지문 (18.7절) |
| 환경 | 파이썬·PyTorch 버전, CPU·GPU | 끝자리가 달라지거나 오류가 난다 | 환경 기록, `uv.lock` (18.7절) |
| 난수 | 씨앗, 섞는 순서, 드롭아웃 | 같은 설정이어도 1%p쯤 흔들린다 | 씨앗 고정, 여러 씨앗 (18.3절, 18.6절) |
| 결과 | 에폭별 손실·정확도, 모델 파일 | 무엇이 좋았는지 비교할 수 없다 | 기록 도구, 체크포인트 (18.3절, 18.4절) |

여섯 가지 중 하나라도 빠지면 그 실험은 "한 번 그랬던 일"이 됩니다. 과학 실험실에서 실험 노트를 쓰는 이유와 같아요. 노트에는 결과만 적지 않고 시약의 제조 번호, 온도, 날짜를 함께 적습니다. 그래야 결과가 이상할 때 원인을 거꾸로 짚어 갈 수 있으니까요.

재현성에도 단계가 있습니다. 가장 쉬운 것은 **내 컴퓨터에서 같은 코드를 다시 돌리면 같은 숫자가 나오는 것**입니다. 씨앗과 섞는 순서를 고정하면 됩니다. 그다음은 **다른 컴퓨터에서 돌려도 비슷한 숫자가 나오는 것**이에요. 8장 8.10절에서 본 것처럼 CPU와 GPU, PyTorch 버전이 다르면 끝자리가 달라질 수 있어서, 환경을 기록해 두고 "비슷한"의 범위를 알아야 합니다. 가장 어려운 것은 **다른 사람이 같은 결론에 이르는 것**입니다. 씨앗 하나에서 우연히 나온 차이를 "개선"이라고 보고하면, 다른 사람이 다시 해 봤을 때 그 개선이 사라져요. 이 장의 뒤쪽에서 이 세 번째 단계를 위해 여러 씨앗으로 실험하는 법을 다룹니다.

## 18.2 설정을 코드 밖으로

### dataclass로 설정 묶기

설정값이 코드 곳곳에 흩어져 있으면 무엇을 바꿨는지 추적하기 어렵습니다. 학습률은 옵티마이저를 만드는 줄에, 배치 크기는 `DataLoader`를 만드는 줄에, 에폭은 `for` 문에 숨어 있죠. 먼저 이 값들을 **한 상자에** 모으겠습니다. 1권 8장의 `dataclass`가 딱 맞는 그릇이에요.

```python
import json
from dataclasses import asdict, dataclass, fields, replace


@dataclass(frozen=True)
class 학습설정:
    """실험 하나를 정하는 값들. 기본값이 곧 '기준 실험'이다."""
    모델: str = "mlp"
    학습률: float = 1e-3
    배치_크기: int = 64
    에폭: int = 2
    드롭아웃: float = 0.0
    씨앗: int = 0


기준 = 학습설정()
print(기준)

# 기준에서 한두 개만 바꾼 실험들: 원본은 그대로 두고 새 설정을 만든다
후보들 = [replace(기준, 학습률=학습률) for 학습률 in (3e-4, 1e-3, 3e-3)]
후보들.append(replace(기준, 모델="cnn", 드롭아웃=0.3))
for 설정 in 후보들:
    print(설정.모델, 설정.학습률, 설정.드롭아웃)

try:
    기준.학습률 = 0.1                       # frozen=True: 실험 도중에 몰래 바꿀 수 없다
except Exception as e:
    print("바꾸기 실패:", type(e).__name__)

# 딕셔너리로 바꾸면 JSON으로 저장할 수 있다
글 = json.dumps(asdict(후보들[-1]), ensure_ascii=False)
print(글)
다시 = 학습설정(**json.loads(글))
print("저장했다 불러와도 같은가:", 다시 == 후보들[-1])
print("필드 이름:", [f.name for f in fields(학습설정)])
```

```text
학습설정(모델='mlp', 학습률=0.001, 배치_크기=64, 에폭=2, 드롭아웃=0.0, 씨앗=0)
mlp 0.0003 0.0
mlp 0.001 0.0
mlp 0.003 0.0
cnn 0.001 0.3
바꾸기 실패: FrozenInstanceError
{"모델": "cnn", "학습률": 0.001, "배치_크기": 64, "에폭": 2, "드롭아웃": 0.3, "씨앗": 0}
저장했다 불러와도 같은가: True
필드 이름: ['모델', '학습률', '배치_크기', '에폭', '드롭아웃', '씨앗']
```

기본값으로 만든 `학습설정()`이 곧 **기준 실험**입니다. 다른 실험은 `dataclasses.replace`로 기준에서 한두 값만 바꿔 만들었어요. `replace`는 원본을 고치지 않고 바뀐 값을 가진 새 설정을 돌려줍니다. 그래서 "기준 대비 무엇을 바꿨는가"가 코드에 그대로 드러나요.

`frozen=True`도 눈여겨보세요. 설정을 만든 뒤에는 값을 바꿀 수 없게 막아 둡니다. 학습 도중에 누군가 `설정.학습률 = 0.1`을 실행하면, 기록에 남은 학습률과 실제로 쓴 학습률이 달라지는 사고가 나거든요. 바꾸려 하면 `FrozenInstanceError`가 납니다.

마지막 부분은 `asdict`로 설정을 딕셔너리로 바꿔 JSON 글자로 만들고, 그 글자에서 다시 설정을 만든 것입니다. 둘이 `==`로 같다고 나왔어요. 설정을 파일로 저장했다가 그대로 되살릴 수 있다는 뜻이고, 이것이 실험 기록의 첫걸음입니다.

### YAML 파일에서 읽기

실험을 바꿀 때마다 파이썬 코드를 고치는 대신 **설정 파일**만 바꾸면 편합니다. 딥러닝 프로젝트에서는 사람이 읽고 쓰기 쉬운 YAML 형식을 많이 써요. `이름: 값`을 한 줄에 하나씩 적고, `#` 뒤는 주석입니다. PyYAML 패키지의 `yaml.safe_load`로 읽으면 딕셔너리가 됩니다.

```python
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
```

```text
{'모델': 'cnn', '학습률': '3e-4', '드롭아웃': 0.3}
학습률의 자료형: str
학습설정(모델='cnn', 학습률=0.0003, 배치_크기=64, 에폭=2, 드롭아웃=0.3, 씨앗=0)
KeyError "모르는 설정 이름: ['학습율']"
TypeError 에폭은(는) int이어야 하는데 '열'
```

출력의 두 번째 줄을 보세요. `학습률: 3e-4`라고 적었는데 실수가 아니라 **글자(str)** `'3e-4'`로 읽혔습니다. 같은 파일의 `드롭아웃: 0.3`은 실수로 잘 읽혔는데 말이죠. PyYAML이 따르는 YAML 1.1 규칙에서는 지수 표기에 소수점이 있어야(`3.0e-4`) 실수로 보기 때문입니다. 이 글자를 그대로 옵티마이저에 넘기면 학습을 시작하는 순간 오류가 나거나, 더 나쁘면 엉뚱한 곳에서 조용히 틀린 값으로 쓰일 수 있어요.

그래서 파일에서 읽은 값은 **검사를 거쳐서** 설정으로 바꿉니다. `설정_만들기`는 dataclass의 필드 목록(`fields`)과 각 필드의 자료형을 보고 세 가지를 합니다. 모르는 이름이 있으면 `KeyError`(마지막 두 줄의 `학습율`처럼 오타를 잡아 줘요), 실수 자리에 글자나 정수가 오면 실수로 바꾸기, 그래도 자료형이 맞지 않으면 `TypeError`입니다. 오타 난 설정 이름을 조용히 무시하면 "학습률을 바꿨는데 결과가 그대로"인 실험을 몇 시간씩 돌리게 됩니다. 1권 8장 8.5절의 Pydantic을 쓰면 이런 검사를 더 짧게 쓸 수 있어요.

### 명령줄에서 덮어쓰기

설정 파일을 만들어 두고도, 학습률 하나만 바꿔서 빨리 돌려 보고 싶을 때가 많습니다. 그럴 때마다 YAML 파일을 복사해 고치기는 번거롭죠. 실행할 때 `uv run python 학습.py --설정 설정_cnn.yaml --학습률 0.001`처럼 **명령줄 인자**로 덮어쓰게 해 두면 편합니다. 표준 라이브러리의 `argparse`가 이 일을 합니다.

```python
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
```

```text
학습설정(모델='mlp', 학습률=0.001, 배치_크기=64, 에폭=2, 드롭아웃=0.0, 씨앗=0)
학습설정(모델='cnn', 학습률=0.0003, 배치_크기=64, 에폭=2, 드롭아웃=0.3, 씨앗=0)
학습설정(모델='cnn', 학습률=0.001, 배치_크기=64, 에폭=2, 드롭아웃=0.3, 씨앗=7)
{'모델': 'mlp', '학습률': 0.001, '배치_크기': 64, '에폭': 5, '드롭아웃': 0.0, '씨앗': 0}
usage: 학습.py [-h] [--설정 설정] [--모델 모델] [--학습률 학습률] [--배치_크기 배치_크기] [--에폭 에폭]
             [--드롭아웃 드롭아웃] [--씨앗 씨앗]
```

`명령줄_해석기`는 dataclass의 필드를 돌면서 `--학습률`, `--에폭` 같은 옵션을 자동으로 만듭니다. 필드를 하나 늘리면 옵션도 저절로 늘어나요. 옵션의 기본값을 `None`으로 둔 것이 요령입니다. `None`이면 "명령줄에서 말하지 않았다"는 뜻이라 아래 단계의 값을 그대로 두고, 값이 있을 때만 덮어씁니다.

출력을 위에서부터 보면 덮어쓰는 순서가 보입니다. 아무 인자도 없으면 기본값, `--설정`을 주면 YAML의 세 값이 기본값을 덮고, 거기에 `--학습률 0.001 --씨앗 7`을 더하면 그 둘만 다시 덮어요. **기본값 < 설정 파일 < 명령줄**, 오른쪽으로 갈수록 힘이 셉니다. 1권 17장의 "설정 관리와 환경별 구성"에서 기본값 위에 환경별 파일을 덮어쓰던 것과 같은 생각이에요. 마지막 두 줄의 사용법 안내는 `-h`를 주면 볼 수 있는 내용으로, `argparse`가 만들어 줍니다.

여기서 하나만 주의하세요. 명령줄로 덮어쓴 값은 파일에 남지 않습니다. 그래서 다음에 볼 실험 폴더에는 **최종으로 합쳐진 설정**을 꼭 저장해야 해요.

### 이 장의 실험 도구

이제 이 장의 예제들이 함께 쓸 도구를 한 파일에 모으겠습니다. 8장의 `학습도구.py`, 9장의 `옷도구.py`와 같은 방식이에요. 아래 내용을 `실험도구.py`로 저장하세요.

```python
"""18장 예제에서 함께 쓰는 설정·데이터·모델·학습 도구."""
import os
import random
from dataclasses import dataclass

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from torchvision import datasets

데이터_폴더 = os.environ.get("BOOK_DATA_DIR", "data")    # 2장부터 써 온 데이터 폴더 설정


@dataclass
class 학습설정:
    """실험 하나를 정하는 값들. 코드와 이 값이 같으면 결과도 같아야 한다."""
    모델: str = "mlp"             # "mlp"(6장) 또는 "cnn"(9장)
    학습률: float = 1e-3
    배치_크기: int = 64
    에폭: int = 2
    드롭아웃: float = 0.0
    가중치_감쇠: float = 0.0
    학습_개수: int = 55_000       # 노트북에서 빨리 돌려 볼 때는 줄인다
    씨앗: int = 0


def 씨앗_고정(씨앗: int) -> None:
    """8장 8.10절: 파이썬·NumPy·PyTorch의 난수 씨앗을 한꺼번에 고정한다."""
    random.seed(씨앗)
    np.random.seed(씨앗)
    torch.manual_seed(씨앗)


def 옷_데이터(학습_개수: int = 55_000, 검증_개수: int = 5_000):
    """FashionMNIST를 텐서로 읽어 학습·검증·시험으로 나눈다. 나누는 방법은 언제나 같다."""
    학습셋 = datasets.FashionMNIST(데이터_폴더, train=True, download=True)
    시험셋 = datasets.FashionMNIST(데이터_폴더, train=False, download=True)
    X, y = 학습셋.data.float().unsqueeze(1) / 255, 학습셋.targets
    순서 = torch.randperm(len(X), generator=torch.Generator().manual_seed(0))
    검증, 학습 = 순서[:검증_개수], 순서[검증_개수:검증_개수 + 학습_개수]
    X_시험 = 시험셋.data.float().unsqueeze(1) / 255
    return (X[학습], y[학습]), (X[검증], y[검증]), (X_시험, 시험셋.targets)


def 모델_만들기(설정: 학습설정) -> nn.Sequential:
    """설정에 적힌 이름으로 6장의 MLP나 9장의 CNN을 만든다."""
    if 설정.모델 == "mlp":
        몸통 = [nn.Flatten(), nn.Linear(28 * 28, 256), nn.ReLU(), nn.Linear(256, 128), nn.ReLU()]
        마지막 = 128
    elif 설정.모델 == "cnn":
        몸통 = [nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
               nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
               nn.Flatten(), nn.Linear(64 * 7 * 7, 128), nn.ReLU()]
        마지막 = 128
    else:
        raise ValueError(f"모르는 모델 이름: {설정.모델}")
    if 설정.드롭아웃 > 0:
        몸통.append(nn.Dropout(설정.드롭아웃))
    return nn.Sequential(*몸통, nn.Linear(마지막, 10))


def 로더_만들기(X: torch.Tensor, y: torch.Tensor, 배치_크기: int, 씨앗: int) -> DataLoader:
    """섞는 순서를 자기 생성기로 정하는 DataLoader (4장 4.1절, 7장)."""
    생성기 = torch.Generator().manual_seed(씨앗)
    return DataLoader(TensorDataset(X, y), batch_size=배치_크기, shuffle=True, generator=생성기)


def 한_에폭_학습(모델: nn.Module, 로더: DataLoader, 옵티마이저: torch.optim.Optimizer) -> float:
    """한 바퀴 학습하고 평균 손실을 돌려준다."""
    모델.train()
    손실_합, 개수 = 0.0, 0
    for x, y in 로더:
        옵티마이저.zero_grad()
        손실 = nn.functional.cross_entropy(모델(x), y)
        손실.backward()
        옵티마이저.step()
        손실_합 += 손실.item() * len(y)
        개수 += len(y)
    return 손실_합 / 개수


@torch.no_grad()
def 평가(모델: nn.Module, X: torch.Tensor, y: torch.Tensor) -> tuple[float, float]:
    """손실과 정확도를 돌려준다. 메모리를 아끼려고 1,000장씩 나눠 계산한다."""
    모델.eval()
    출력 = torch.cat([모델(X[i:i + 1000]) for i in range(0, len(X), 1000)])
    return nn.functional.cross_entropy(출력, y).item(), (출력.argmax(dim=1) == y).float().mean().item()
```

`학습설정`은 앞의 설정에 `가중치_감쇠`(8장 8.2절)와 `학습_개수`를 더한 것입니다. 노트북에서 실험을 여러 번 빨리 돌리려고 학습 사진 수를 줄일 수 있게 했어요. 이번에는 `frozen=True`를 빼서 실습 중에 값을 바꿔 보기 쉽게 했지만, 실제 프로젝트에서는 붙여 두기를 권합니다.

`옷_데이터`는 FashionMNIST 학습 사진 6만 장을 고정된 순서로 섞어서 앞의 5,000장을 검증용, 그다음 `학습_개수`장을 학습용으로 씁니다. 시험 데이터 1만 장은 따로 두고요. 사진마다 변환을 거치지 않고 처음부터 텐서로 바꿔 7장 7.2절의 `TensorDataset`에 담기 때문에 빠릅니다. `모델_만들기`는 설정의 `모델` 값을 보고 6장의 MLP나 9장의 CNN을 같은 구조로 만들어요. `로더_만들기`는 섞는 순서를 자기 생성기로 정하는 `DataLoader`이고, 이 생성기가 다음 절의 주인공입니다.

### 설정마다 실험 폴더 하나

설정이 정해지면 실험 결과를 담을 폴더를 만듭니다. 폴더 이름에 날짜를 붙이는 사람도 많지만, 여기서는 **설정의 지문**을 붙여 보겠습니다. 설정이 같으면 지문도 같으니, 같은 실험을 두 번 돌리는 일을 막을 수 있어요.

```python
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
```

```text
기준 지문     : 865b758e
다시 만들어도 : 865b758e
씨앗만 바꿔도 : 60be0fbc
새 폴더: runs/mlp_lr0.001_s0_865b758e
새 폴더: runs/mlp_lr0.003_s0_8f62ef74
이미 한 실험이라 건너뜀
모델: mlp
학습률: 0.001
배치_크기: 64
에폭: 2
드롭아웃: 0.0
가중치_감쇠: 0.0
학습_개수: 55000
씨앗: 0

```

`설정_지문`은 설정을 JSON 글자로 바꾼 뒤 SHA-256 해시의 앞 8글자를 씁니다. `hashlib`은 어떤 글자든 받아서 고정된 길이의 "지문"을 만드는 표준 라이브러리예요. 입력이 한 글자만 달라도 지문이 완전히 달라지고, 같은 입력은 언제 어디서 계산해도 같은 지문이 나옵니다. `sort_keys=True`로 이름 순서를 고정한 것도 중요해요. 같은 설정인데 딕셔너리 순서 때문에 지문이 달라지면 안 되니까요.

결과를 보면 다시 만든 기본 설정은 지문이 같고(`865b758e`), 씨앗만 바꿔도 지문이 달라졌습니다. 세 번째로 기준 설정을 다시 넣었을 때는 폴더가 이미 있어서 건너뛰었어요. 폴더 안의 `설정.yaml`에는 합쳐진 최종 설정이 모두 들어 있습니다. 나중에 이 폴더만 보고도 "이 결과는 어떤 설정이었나"에 답할 수 있어요.

## 18.3 체크포인트와 재개

### 모델과 옵티마이저만으로는 부족합니다

몇 시간짜리 학습이 중간에 멈추는 일은 생각보다 흔합니다. 노트북 덮개를 닫거나, 전원이 나가거나, 공용 GPU 서버의 사용 시간이 끝나거나요. 6장 6.10절에서 에폭 번호, 모델 상태, 옵티마이저 상태를 체크포인트에 담아 이어서 학습하는 법을 봤습니다. 그런데 정말 그것으로 충분할까요? 4에폭을 한 번에 학습한 결과와, 2에폭 하고 6장처럼 저장한 뒤 프로그램을 새로 켜서 2에폭을 더 한 결과를 비교해 보겠습니다. 8장 8.7절의 코사인 스케줄러와 8.3절의 드롭아웃을 넣었어요.

```python
import torch
from torch.optim.lr_scheduler import CosineAnnealingLR

from 실험도구 import 로더_만들기, 모델_만들기, 씨앗_고정, 옷_데이터, 평가, 학습설정, 한_에폭_학습

설정 = 학습설정(드롭아웃=0.2, 에폭=4, 학습_개수=10_000)
(X_학습, y_학습), (X_검증, y_검증), _ = 옷_데이터(설정.학습_개수)


def 학습_준비():
    """프로그램을 새로 켰을 때처럼 모든 것을 처음부터 만든다."""
    씨앗_고정(설정.씨앗)
    모델 = 모델_만들기(설정)
    옵티마이저 = torch.optim.Adam(모델.parameters(), lr=설정.학습률)
    스케줄러 = CosineAnnealingLR(옵티마이저, T_max=설정.에폭)
    로더 = 로더_만들기(X_학습, y_학습, 설정.배치_크기, 설정.씨앗)
    return 모델, 옵티마이저, 스케줄러, 로더


def 에폭_돌기(시작: int, 끝: int, 모델, 옵티마이저, 스케줄러, 로더) -> list[float]:
    """시작~끝 에폭을 학습하고, 에폭마다 쓴 학습률을 돌려준다."""
    쓴_학습률 = []
    for 에폭 in range(시작, 끝 + 1):
        쓴_학습률.append(round(옵티마이저.param_groups[0]["lr"], 6))
        한_에폭_학습(모델, 로더, 옵티마이저)
        스케줄러.step()
    return 쓴_학습률


# 1) 한 번에 4에폭
모델, 옵티마이저, 스케줄러, 로더 = 학습_준비()
학습률들 = 에폭_돌기(1, 4, 모델, 옵티마이저, 스케줄러, 로더)
한번에 = 모델.state_dict()
print(f"한 번에 4에폭       : 검증 정확도 {평가(모델, X_검증, y_검증)[1]:.2%}, 학습률 {학습률들}")

# 2) 2에폭 하고 6장 6.10절처럼 저장 → 프로그램을 새로 켜서 불러오고 2에폭 더
모델, 옵티마이저, 스케줄러, 로더 = 학습_준비()
앞 = 에폭_돌기(1, 2, 모델, 옵티마이저, 스케줄러, 로더)
torch.save({"에폭": 2, "모델": 모델.state_dict(), "옵티마이저": 옵티마이저.state_dict()}, "중간.pt")

모델, 옵티마이저, 스케줄러, 로더 = 학습_준비()          # 새로 켠 프로그램
상자 = torch.load("중간.pt", weights_only=True)
모델.load_state_dict(상자["모델"])
옵티마이저.load_state_dict(상자["옵티마이저"])
뒤 = 에폭_돌기(상자["에폭"] + 1, 4, 모델, 옵티마이저, 스케줄러, 로더)
print(f"2에폭 + 이어서 2에폭: 검증 정확도 {평가(모델, X_검증, y_검증)[1]:.2%}, 학습률 {앞 + 뒤}")
같은가 = all(torch.equal(한번에[k], v) for k, v in 모델.state_dict().items())
print("가중치가 같은가:", 같은가)
```

```text
한 번에 4에폭       : 검증 정확도 84.32%, 학습률 [0.001, 0.000854, 0.0005, 0.000146]
2에폭 + 이어서 2에폭: 검증 정확도 84.24%, 학습률 [0.001, 0.000854, 0.0005, 0.000427]
가중치가 같은가: False
```

두 결과의 검증 정확도가 84.32%와 84.24%로 다르고, 가중치도 같지 않습니다. 이어서 한 학습은 한 번에 한 학습을 **재현하지 못했어요.** 원인은 세 가지입니다.

- **스케줄러**: 출력의 학습률 목록을 보세요. 한 번에 학습하면 네 번째 에폭의 학습률이 0.000146인데, 이어서 학습하면 0.000427입니다. 새로 만든 스케줄러는 자기가 몇 번째 에폭에 있는지 모르고, 코사인 곡선의 처음부터 다시 계산했기 때문이에요.
- **섞는 순서**: 새로 만든 `DataLoader`의 생성기가 처음 상태로 돌아가서, 3에폭째에 1에폭과 같은 순서로 데이터를 섞었습니다. 한 번에 학습했다면 3에폭째에는 세 번째 순서가 나왔겠죠.
- **드롭아웃의 난수**: 드롭아웃이 어떤 칸을 끌지는 PyTorch의 전역 난수가 정합니다. 새 프로그램에서 씨앗을 다시 심었으니, 3에폭째의 난수 줄이 한 번에 학습할 때와 달라졌어요.

차이가 0.08%p뿐이라 별일 아닌 것 같지만, 이 차이가 있는 한 "중간에 끊겼던 실험"과 "끊기지 않은 실험"을 같은 실험이라고 말할 수 없습니다. 끊긴 횟수와 위치에 따라 결과가 바뀌는 실험은 재현할 수 없어요.

### 다시 켜도 똑같이 이어 가기

그럼 이 세 가지 상태까지 모두 담으면 되겠죠. 스케줄러는 옵티마이저처럼 `state_dict()`가 있고, `DataLoader`의 생성기와 난수 발생기는 `get_state()`로 지금 상태를 꺼낼 수 있습니다. 내친김에 실제로 학습 도중 "정전"을 일으켜 보겠습니다.

```python
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
```

```text
[한 번에]
  에폭 1: 검증 정확도 77.44%, 학습률 0.000854
  에폭 2: 검증 정확도 81.70%, 학습률 0.000500
  에폭 3: 검증 정확도 82.64%, 학습률 0.000146
  에폭 4: 검증 정확도 84.32%, 학습률 0.000000
[중간에 꺼졌다가 다시]
  에폭 1: 검증 정확도 77.44%, 학습률 0.000854
  에폭 2: 검증 정확도 81.70%, 학습률 0.000500
  오류: 3에폭 도중 정전!
  2에폭 체크포인트에서 이어 갑니다
  에폭 3: 검증 정확도 82.64%, 학습률 0.000146
  에폭 4: 검증 정확도 84.32%, 학습률 0.000000
가중치가 같은가: True
체크포인트에 담은 것: ['에폭', '모델', '옵티마이저', '스케줄러', '섞기_생성기', '난수', '최고_정확도']
파일 크기: last.pt 2781KB, best.pt 921KB
```

3에폭 학습은 마쳤지만 아직 체크포인트를 저장하기 전, 즉 3에폭을 마무리하는 도중에 오류를 일으켜 프로그램이 죽은 상황을 흉내 냈습니다. 다시 `학습`을 부르자 `last.pt`를 찾아 2에폭 체크포인트에서 이어 갔고, 3·4에폭의 검증 정확도와 학습률이 한 번에 학습한 것과 똑같습니다. 마지막에 가중치를 비교하니 `True`예요. 이제 몇 번을 끊겼다 이어 가도 같은 실험입니다.

체크포인트에 담은 일곱 가지 중 새로 더한 것은 이렇습니다.

| 담은 것 | 꺼내기 | 되돌리기 | 빠지면 |
|---|---|---|---|
| 스케줄러 | `스케줄러.state_dict()` | `load_state_dict` | 학습률이 처음부터 다시 계산됨 |
| 섞기 생성기 | `로더.generator.get_state()` | `set_state` | 섞는 순서가 1에폭부터 반복됨 |
| 전역 난수 | `torch.get_rng_state()` 등 | `torch.set_rng_state()` 등 | 드롭아웃·증강의 무작위가 달라짐 |
| 최고 점수 | 숫자 하나 | 그대로 | 조기 종료·최고 모델 판단이 틀어짐 |

코드에서 짚어 둘 곳이 세 군데 있습니다.

- **NumPy 난수 상태**: `np.random.get_state()`는 NumPy 배열을 담은 튜플을 돌려주는데, 이것을 그대로 저장하면 `torch.load(..., weights_only=True)`가 거부합니다. 6장 6.10절에서 본 안전장치가 NumPy 배열을 "텐서도 기본 자료형도 아닌 것"으로 보기 때문이에요. 그래서 `난수_상태`에서 `.tolist()`로 바꿔 저장하고, 되돌릴 때 다시 배열로 만들었습니다. 안전장치를 끄는(`weights_only=False`) 쉬운 길보다 이쪽이 낫습니다.
- **안전하게 저장하기**: `안전하게_저장`은 `.tmp` 파일에 다 쓴 다음 `os.replace`로 이름을 바꿉니다. `torch.save`가 파일을 반쯤 쓰다가 전원이 나가면 체크포인트가 깨져서 열리지 않는데, 이렇게 하면 마지막 순간까지 예전 `last.pt`가 멀쩡히 남아 있어요. 이름 바꾸기는 한 번에 일어나서 "반쯤 바뀐" 상태가 없습니다.
- **last와 best**: `last.pt`는 이어 가기용으로 매 에폭 덮어쓰고, `best.pt`는 검증 정확도가 좋아질 때만 모델만 저장합니다. 8장 8.8절의 조기 종료에서 "가장 좋았던 순간의 가중치"를 메모리에 두던 것을 파일로 옮긴 셈이에요. 파일 크기를 보면 `last.pt`가 `best.pt`의 세 배쯤 됩니다. Adam이 파라미터마다 두 가지 평균을 기억해서(6장 6.10절), 옵티마이저 상태가 모델보다 두 배 크기 때문입니다.

> **Q. 체크포인트는 얼마나 자주 저장해야 하나요?**
> "잃어도 괜찮은 시간"으로 정하세요. 한 에폭이 몇 분이면 에폭마다, 한 에폭이 몇 시간이면 몇백 스텝마다 저장합니다. 스텝 단위로 저장할 때는 에폭 번호 대신 "몇 번째 배치까지 했는지"도 담아야 하고, 그 에폭 안에서 이미 지나간 배치를 건너뛰어야 정확히 이어집니다. 디스크가 걱정되면 `last.pt` 하나만 덮어쓰고, `best.pt`와 에폭별 파일은 꼭 필요한 것만 남기세요.

## 18.4 실험 기록 남기기

### 직접 만드는 기록장: JSON Lines

학습 중의 손실과 정확도를 `print`로만 보면 터미널을 닫는 순간 사라집니다. 가장 간단한 기록 방법은 **에폭마다 한 줄씩 파일에 덧붙이는 것**이에요. 한 줄에 JSON 하나를 쓰는 이 형식을 **JSON Lines**라고 부르고, 확장자는 보통 `.jsonl`입니다.

```python
import json
from pathlib import Path

import torch

from 실험도구 import 로더_만들기, 모델_만들기, 씨앗_고정, 옷_데이터, 평가, 학습설정, 한_에폭_학습


class 기록장:
    """에폭마다 한 줄씩 JSON으로 덧붙여 쓰는 기록 파일 (JSON Lines)."""

    def __init__(self, 파일: Path) -> None:
        파일.parent.mkdir(parents=True, exist_ok=True)
        self.파일 = 파일.open("a", encoding="utf-8")

    def 적기(self, **값) -> None:
        self.파일.write(json.dumps(값, ensure_ascii=False) + "\n")
        self.파일.flush()                  # 학습이 중간에 죽어도 여기까지는 남는다

    def __enter__(self) -> "기록장":
        return self

    def __exit__(self, *오류) -> None:
        self.파일.close()


설정 = 학습설정(에폭=4, 학습_개수=10_000)
(X_학습, y_학습), (X_검증, y_검증), _ = 옷_데이터(설정.학습_개수)
씨앗_고정(설정.씨앗)
모델 = 모델_만들기(설정)
옵티마이저 = torch.optim.Adam(모델.parameters(), lr=설정.학습률)
로더 = 로더_만들기(X_학습, y_학습, 설정.배치_크기, 설정.씨앗)

with 기록장(Path("runs/기록연습/기록.jsonl")) as 기록:
    for 에폭 in range(1, 설정.에폭 + 1):
        학습_손실 = 한_에폭_학습(모델, 로더, 옵티마이저)
        검증_손실, 검증_정확도 = 평가(모델, X_검증, y_검증)
        기록.적기(에폭=에폭, 학습_손실=round(학습_손실, 4), 검증_손실=round(검증_손실, 4),
                 검증_정확도=round(검증_정확도, 4))

줄들 = Path("runs/기록연습/기록.jsonl").read_text(encoding="utf-8").splitlines()
print(줄들[0])
기록들 = [json.loads(줄) for 줄 in 줄들]
최고 = max(기록들, key=lambda r: r["검증_정확도"])
print(f"{len(기록들)}줄 기록, 가장 좋았던 에폭 {최고['에폭']}: {최고['검증_정확도']:.2%}")
```

```text
{"에폭": 1, "학습_손실": 0.8527, "검증_손실": 0.6118, "검증_정확도": 0.7756}
4줄 기록, 가장 좋았던 에폭 4: 84.52%
```

`기록장`은 파일을 덧붙이기 모드(`"a"`)로 열고, `적기`를 부를 때마다 JSON 한 줄을 씁니다. 1권 12장에서 본 `with` 문으로 쓸 수 있게 `__enter__`와 `__exit__`를 넣어서 학습이 끝나면 파일이 저절로 닫혀요. JSON 하나짜리 파일 대신 줄마다 따로 쓰는 이유는 **중간에 죽어도 거기까지는 남기 때문**입니다. `flush()`로 매번 디스크에 밀어내니, 3에폭째에 프로그램이 죽어도 1·2에폭의 기록은 파일에 있어요. 읽을 때는 한 줄씩 `json.loads`하면 딕셔너리 목록이 됩니다.

덧붙이기 모드라서 같은 파일로 다시 실행하면 기록이 뒤에 이어 붙습니다. 18.2절처럼 실험마다 폴더를 따로 두면 이 문제가 없어요. 이 정도 기록장만 있어도 혼자 하는 작은 프로젝트에는 충분합니다. 그런데 실험이 수십 개가 되면 곡선을 겹쳐 보고 표로 정렬하는 일이 번거로워지죠. 그때 쓰는 것이 기록 도구입니다.

### TensorBoard: 곡선을 겹쳐 보기

**TensorBoard**는 원래 TensorFlow와 함께 나온 오픈소스 시각화 도구인데, PyTorch에 기록용 `SummaryWriter`가 들어 있어서 그대로 쓸 수 있습니다. 학습률 두 가지로 학습하며 기록해 보겠습니다.

```python
from dataclasses import asdict, replace

import torch
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
from torch.utils.tensorboard import SummaryWriter

from 실험도구 import 로더_만들기, 모델_만들기, 씨앗_고정, 옷_데이터, 평가, 학습설정, 한_에폭_학습

기준 = 학습설정(에폭=4, 학습_개수=10_000)
(X_학습, y_학습), (X_검증, y_검증), _ = 옷_데이터(기준.학습_개수)

for 학습률 in (1e-3, 1e-2):
    설정 = replace(기준, 학습률=학습률)
    씨앗_고정(설정.씨앗)
    모델 = 모델_만들기(설정)
    옵티마이저 = torch.optim.Adam(모델.parameters(), lr=설정.학습률)
    로더 = 로더_만들기(X_학습, y_학습, 설정.배치_크기, 설정.씨앗)
    with SummaryWriter(f"tb/lr{학습률:g}") as 쓰개:           # 실험마다 폴더 하나
        for 에폭 in range(1, 설정.에폭 + 1):
            학습_손실 = 한_에폭_학습(모델, 로더, 옵티마이저)
            검증_손실, 검증_정확도 = 평가(모델, X_검증, y_검증)
            쓰개.add_scalar("손실/학습", 학습_손실, 에폭)       # 이름의 / 앞이 같으면 한 칸에 모인다
            쓰개.add_scalar("손실/검증", 검증_손실, 에폭)
            쓰개.add_scalar("정확도/검증", 검증_정확도, 에폭)
        쓰개.add_histogram("가중치/첫층", 모델[1].weight, 에폭)
        쓰개.add_hparams(asdict(설정), {"최종/검증_정확도": 검증_정확도}, run_name=".")

# 파일에 무엇이 들어갔는지 TensorBoard의 읽기 도구로 확인
for 폴더 in ("tb/lr0.001", "tb/lr0.01"):
    읽개 = EventAccumulator(폴더).Reload()
    print(폴더, "→", 읽개.Tags()["scalars"])
    print("  검증 정확도:", [round(e.value, 4) for e in 읽개.Scalars("정확도/검증")])
```

```text
tb/lr0.001 → ['손실/학습', '손실/검증', '정확도/검증', '최종/검증_정확도']
  검증 정확도: [0.7756, 0.8282, 0.834, 0.8452]
tb/lr0.01 → ['손실/학습', '손실/검증', '정확도/검증', '최종/검증_정확도']
  검증 정확도: [0.799, 0.8014, 0.8302, 0.822]
```

`SummaryWriter("tb/lr0.001")`처럼 실험마다 폴더를 하나씩 주고, `add_scalar(이름, 값, 에폭)`으로 숫자를 남깁니다. 이름의 `/` 앞부분이 같으면 화면에서 한 칸에 모여요. `손실/학습`과 `손실/검증`은 "손실" 칸에 나란히 놓입니다. `add_histogram`은 첫 층 가중치의 분포를, `add_hparams`는 설정과 최종 성적을 표로 남겨요.

TensorBoard의 기록은 사람이 읽기 어려운 이진 파일이라, 마지막 부분에서 TensorBoard의 읽기 도구(`EventAccumulator`)로 무엇이 들어갔는지 확인했습니다. 학습률 0.001은 정확도가 꾸준히 올라 84.52%가 됐고, 0.01은 첫 에폭에 79.90%로 더 빨리 올랐지만 4에폭째에 83.02%에서 82.20%로 도로 내려갔어요. 학습률이 크면 처음엔 빠르지만 끝에서 흔들린다는 8장 8.7절의 이야기 그대로입니다.

화면으로 보려면 터미널에서 TensorBoard를 띄웁니다. 이 책의 환경에서 실제로 실행한 명령과 출력이에요.

```text
$ uv run tensorboard --logdir tb
TensorFlow installation not found - running with reduced feature set.
Serving TensorBoard on localhost; to expose to the network, use a proxy or pass --bind_all
TensorBoard 2.21.0 at http://localhost:6006/ (Press CTRL+C to quit)
```

첫 줄은 TensorFlow 없이 PyTorch 기록만 보여 준다는 안내라 신경 쓰지 않아도 됩니다. 웹 브라우저로 `http://localhost:6006/`을 열면 Scalars(또는 Time Series) 탭에서 두 실험의 곡선이 색을 달리해 겹쳐 그려지고, Histograms 탭에서 가중치 분포를, HParams 탭에서 설정별 성적을 표로 볼 수 있어요. 학습이 진행되는 동안에도 몇 초 간격으로 새 기록을 읽어 와 곡선이 자랍니다. 다 보면 터미널에서 `Ctrl+C`로 끕니다.

### MLflow: 실험을 표로 찾고 비교하기

TensorBoard가 곡선을 보는 데 강하다면, **MLflow**는 실험을 **데이터베이스처럼 저장하고 찾는 데** 강한 오픈소스 도구입니다. 설정(파라미터), 에폭별 숫자(메트릭), 메모(태그), 모델 같은 파일(아티팩트)을 실험 단위로 묶어 두고, 나중에 조건으로 찾아 표로 꺼낼 수 있어요. 기록은 1권 18장에서 배운 SQLite 파일 하나에 담기게 하겠습니다.

```python
from dataclasses import asdict, replace

import mlflow
import torch

from 실험도구 import 로더_만들기, 모델_만들기, 씨앗_고정, 옷_데이터, 평가, 학습설정, 한_에폭_학습

mlflow.set_tracking_uri("sqlite:///mlflow.db")        # 기록은 이 폴더의 SQLite 파일 하나에
mlflow.set_experiment("옷분류-학습률")
기준 = 학습설정(에폭=4, 학습_개수=10_000)
(X_학습, y_학습), (X_검증, y_검증), _ = 옷_데이터(기준.학습_개수)

for 학습률 in (3e-4, 1e-3, 3e-3, 1e-2):
    설정 = replace(기준, 학습률=학습률)
    with mlflow.start_run(run_name=f"mlp lr={학습률:g}"):
        mlflow.log_params(asdict(설정))                  # 설정 전부
        mlflow.set_tag("메모", "학습률만 바꿔 본 실험")
        씨앗_고정(설정.씨앗)
        모델 = 모델_만들기(설정)
        옵티마이저 = torch.optim.Adam(모델.parameters(), lr=설정.학습률)
        로더 = 로더_만들기(X_학습, y_학습, 설정.배치_크기, 설정.씨앗)
        for 에폭 in range(1, 설정.에폭 + 1):
            학습_손실 = 한_에폭_학습(모델, 로더, 옵티마이저)
            검증_손실, 검증_정확도 = 평가(모델, X_검증, y_검증)
            mlflow.log_metrics({"학습_손실": 학습_손실, "검증_손실": 검증_손실,
                                "검증_정확도": 검증_정확도}, step=에폭)
        torch.save(모델.state_dict(), "모델.pt")
        mlflow.log_artifact("모델.pt")                   # 파일도 실험에 붙여 둔다

# 기록을 표로 꺼내 비교하기 (pandas DataFrame)
표 = mlflow.search_runs(experiment_names=["옷분류-학습률"], order_by=["metrics.검증_정확도 DESC"])
for _, 줄 in 표.iterrows():
    print(f"{줄['tags.mlflow.runName']:13} 학습률 {줄['params.학습률']:>6}  "
          f"검증 정확도 {줄['metrics.검증_정확도']:.2%}  검증 손실 {줄['metrics.검증_손실']:.4f}")

# 실험 하나의 에폭별 기록과 붙여 둔 파일
최고 = 표.iloc[0]
이력 = mlflow.MlflowClient().get_metric_history(최고.run_id, "검증_정확도")
print("에폭별 검증 정확도:", [(m.step, round(m.value, 4)) for m in 이력])
print("붙여 둔 파일:", [f.path for f in mlflow.MlflowClient().list_artifacts(최고.run_id)])
```

```text
mlp lr=0.003  학습률  0.003  검증 정확도 84.60%  검증 손실 0.4289
mlp lr=0.001  학습률  0.001  검증 정확도 84.52%  검증 손실 0.4395
mlp lr=0.0003 학습률 0.0003  검증 정확도 82.82%  검증 손실 0.4883
mlp lr=0.01   학습률   0.01  검증 정확도 82.20%  검증 손실 0.5008
에폭별 검증 정확도: [(1, 0.8068), (2, 0.8116), (3, 0.825), (4, 0.846)]
붙여 둔 파일: ['모델.pt']
```

`set_experiment`로 실험 묶음의 이름을 정하고, `with mlflow.start_run():` 안에서 기록하면 그 블록이 실험 하나가 됩니다. `log_params(asdict(설정))` 한 줄로 18.2절의 설정을 통째로 남기는 것이 dataclass로 설정을 묶어 둔 덕분이에요. `log_metrics`는 에폭마다, `log_artifact`는 모델 파일을 실험에 붙입니다. 기록은 `mlflow.db`(SQLite)에, 붙인 파일은 `mlruns` 폴더에 저장돼요.

뒷부분이 MLflow의 진가입니다. `search_runs`가 실험 묶음 전체를 pandas 표(1권 20장)로 돌려주고, `order_by`로 마지막 검증 정확도가 높은 순서대로 정렬했어요. 학습률 0.003이 84.60%, 0.001이 84.52%로 거의 같고, 0.0003은 너무 느려서, 0.01은 너무 커서 낮습니다. 가장 좋은 실험의 에폭별 기록과 붙여 둔 파일도 꺼내 봤어요. 실험이 수백 개로 늘어나도 `filter_string="params.모델 = 'cnn'"`처럼 조건을 걸어 찾을 수 있습니다.

MLflow에도 화면이 있습니다. 같은 폴더에서 이렇게 띄워요(이 책의 환경에서 실행한 출력의 마지막 줄만 옮겼습니다).

```text
$ uv run mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5001
... INFO:     Uvicorn running on http://127.0.0.1:5001 (Press CTRL+C to quit)
```

`--backend-store-uri`로 기록이 든 SQLite 파일을 알려 줍니다. 기본 포트는 5000인데, macOS에서는 AirPlay 수신 기능(제어 센터)이 5000번을 쓰고 있을 수 있어서 이 책에서는 `--port 5001`로 바꿨어요. 브라우저에서 `http://127.0.0.1:5001`을 열면 실험 목록이 표로 나오고, 실험 여러 개를 골라 곡선과 설정을 나란히 비교할 수 있습니다. `Uvicorn`이라는 이름이 낯익다면 맞아요, 1권 19장에서 FastAPI 서버를 띄울 때 본 그 서버입니다.

| 도구 | 강한 곳 | 기록이 저장되는 곳 | 이럴 때 |
|---|---|---|---|
| JSON Lines (직접) | 단순함, 의존성 없음 | 실험 폴더의 `.jsonl` | 혼자 하는 작은 실험 |
| TensorBoard | 곡선 겹쳐 보기, 분포 그림 | 이벤트 파일 폴더 | 학습 과정을 실시간으로 볼 때 |
| MLflow | 설정·결과 검색과 비교, 파일 보관 | SQLite 등 데이터베이스 + 파일 폴더 | 실험이 많고 여럿이 함께 볼 때 |

어느 도구를 쓰든 원칙은 같습니다. **설정 전체, 에폭별 숫자, 최종 결과, 모델 파일을 실험 하나로 묶어 둔다.** 도구는 나중에 바꿀 수 있지만, 기록하지 않은 실험은 되살릴 수 없어요.

## 18.5 하이퍼파라미터 탐색 자동화

### Optuna: 지난 결과를 보고 다음 값을 고르기

3장 3.10절에서 `GridSearchCV`로 후보 조합을 모두 시험해 봤습니다. 딥러닝에서는 학습 한 번이 무거워서 조합을 다 돌리기 어렵죠. 학습률·드롭아웃·가중치 감쇠·배치 크기를 네 가지씩만 골라도 256번입니다. 그래서 정해진 횟수 안에서 **영리하게 고르는** 방법을 씁니다.

**Optuna**는 이 일을 해 주는 오픈소스 라이브러리입니다. 우리는 "값을 받아 학습하고 점수를 돌려주는 함수"만 짜면, Optuna가 값을 골라 이 함수를 여러 번 부르며 점수를 키워 가요. 무작위로 고르는 방법과 Optuna의 기본 방법(TPE)을 같은 30번으로 비교해 보겠습니다.

```python
import optuna
import torch

from 실험도구 import 로더_만들기, 모델_만들기, 씨앗_고정, 옷_데이터, 평가, 학습설정, 한_에폭_학습

optuna.logging.set_verbosity(optuna.logging.WARNING)     # 시도마다 찍는 안내 끄기
(X_학습, y_학습), (X_검증, y_검증), _ = 옷_데이터(학습_개수=20_000)


def 목적함수(시도: optuna.Trial) -> float:
    """Optuna가 고른 값으로 학습하고 검증 정확도를 돌려준다. 이 값을 키우는 것이 목표."""
    설정 = 학습설정(
        학습률=시도.suggest_float("학습률", 1e-4, 1e-1, log=True),     # 0.0001~0.1, 로그 눈금
        드롭아웃=시도.suggest_float("드롭아웃", 0.0, 0.5),
        가중치_감쇠=시도.suggest_float("가중치_감쇠", 1e-6, 1e-1, log=True),
        배치_크기=시도.suggest_categorical("배치_크기", [32, 64, 128, 256]),
        에폭=3, 학습_개수=20_000,
    )
    씨앗_고정(설정.씨앗)
    모델 = 모델_만들기(설정)
    옵티마이저 = torch.optim.AdamW(모델.parameters(), lr=설정.학습률, weight_decay=설정.가중치_감쇠)
    로더 = 로더_만들기(X_학습, y_학습, 설정.배치_크기, 설정.씨앗)
    for _ in range(설정.에폭):
        한_에폭_학습(모델, 로더, 옵티마이저)
    return 평가(모델, X_검증, y_검증)[1]


for 이름, 고르개 in [("무작위", optuna.samplers.RandomSampler(seed=0)),
                    ("TPE", optuna.samplers.TPESampler(seed=0))]:
    연구 = optuna.create_study(direction="maximize", sampler=고르개)
    연구.optimize(목적함수, n_trials=30)
    값들 = [t.value for t in 연구.trials]
    print(f"[{이름}] 최고 {연구.best_value:.2%} ({연구.best_trial.number + 1}번째 시도)")
    print("  최고 설정:", {k: (round(v, 5) if isinstance(v, float) else v) for k, v in 연구.best_params.items()})
    print("  처음 10번:", " ".join(f"{v:.3f}" for v in 값들[:10]))
    print("  나중 20번:", " ".join(f"{v:.3f}" for v in 값들[10:]))
    print(f"  나중 20번 평균 {sum(값들[10:]) / 20:.2%}, 80% 미만 {sum(v < 0.8 for v in 값들)}번")
```

```text
[무작위] 최고 85.64% (8번째 시도)
  최고 설정: {'학습률': 0.00123, '드롭아웃': 0.2851, '가중치_감쇠': 0.00016, '배치_크기': 32}
  처음 10번: 0.840 0.614 0.784 0.809 0.845 0.814 0.818 0.856 0.826 0.824
  나중 20번: 0.428 0.801 0.849 0.840 0.789 0.850 0.833 0.780 0.811 0.850 0.417 0.578 0.793 0.849 0.830 0.854 0.851 0.855 0.838 0.815
  나중 20번 평균 77.55%, 80% 미만 8번
[TPE] 최고 86.14% (24번째 시도)
  최고 설정: {'학습률': 0.00099, '드롭아웃': 0.43098, '가중치_감쇠': 0.00065, '배치_크기': 32}
  처음 10번: 0.840 0.614 0.784 0.809 0.845 0.814 0.818 0.856 0.826 0.824
  나중 20번: 0.843 0.854 0.826 0.763 0.857 0.851 0.855 0.852 0.818 0.845 0.848 0.843 0.854 0.861 0.859 0.848 0.855 0.827 0.858 0.859
  나중 20번 평균 84.38%, 80% 미만 3번
```

`목적함수`는 `시도`(trial)에게 값을 물어 설정을 만듭니다. `suggest_float("학습률", 1e-4, 1e-1, log=True)`는 "0.0001부터 0.1 사이에서 하나 골라 줘, 단 로그 눈금으로"라는 뜻이에요. 학습률은 0.0001과 0.001의 차이가 0.09와 0.1의 차이보다 훨씬 중요하니, 자릿수마다 공평하게 고르라고 `log=True`를 줍니다. `suggest_categorical`은 목록에서 하나를 고르고요. 고른 값으로 18.2절의 `학습설정`을 만드니 나머지 학습 코드는 그대로입니다.

두 방법의 **처음 10번이 똑같습니다.** TPE도 처음에는 아는 것이 없어서 무작위로 고르고, 씨앗(`seed=0`)이 같으니 같은 값이 나온 거예요. 차이는 그다음부터입니다. 무작위는 계속 아무 데나 골라서 나중 20번에도 42.8%, 41.7% 같은 실패작이 섞이고 평균이 77.55%입니다. TPE는 지난 결과에서 "점수가 좋았던 값 근처"를 더 자주 골라서 나중 20번의 평균이 84.38%, 최고도 86.14%로 더 높아요. 같은 30번을 돌려도 좋은 곳을 더 많이 들여다본 셈입니다.

TPE가 찾은 최고 설정은 학습률 약 0.001, 드롭아웃 0.43, 배치 크기 32였어요. 학습률 0.001은 6장에서 "Adam의 출발점"으로 권한 값과 거의 같습니다. 탐색은 이렇게 경험칙을 확인해 주기도 하고, 드롭아웃처럼 감으로 정하기 어려운 값을 대신 골라 주기도 합니다.

### 가망 없는 시도는 중간에 멈추기

30번 중에는 첫 에폭부터 성적이 형편없는 시도가 섞여 있습니다. 그런 시도를 끝까지 학습하는 것은 낭비죠. 수능 모의고사 성적이 계속 바닥인 과목에 학원비를 끝까지 내지 않는 것과 비슷합니다. Optuna는 에폭마다 중간 성적을 보고받아, 다른 시도들보다 못하면 **가지치기(pruning)** 로 멈추게 할 수 있어요.

```python
import optuna
import torch

from 실험도구 import 로더_만들기, 모델_만들기, 씨앗_고정, 옷_데이터, 평가, 학습설정, 한_에폭_학습

optuna.logging.set_verbosity(optuna.logging.WARNING)
(X_학습, y_학습), (X_검증, y_검증), _ = 옷_데이터(학습_개수=20_000)
최대_에폭 = 5


def 목적함수(시도: optuna.Trial) -> float:
    설정 = 학습설정(
        학습률=시도.suggest_float("학습률", 1e-4, 1e-1, log=True),
        드롭아웃=시도.suggest_float("드롭아웃", 0.0, 0.5),
        가중치_감쇠=시도.suggest_float("가중치_감쇠", 1e-6, 1e-1, log=True),
        배치_크기=시도.suggest_categorical("배치_크기", [32, 64, 128, 256]),
        에폭=최대_에폭, 학습_개수=20_000,
    )
    씨앗_고정(설정.씨앗)
    모델 = 모델_만들기(설정)
    옵티마이저 = torch.optim.AdamW(모델.parameters(), lr=설정.학습률, weight_decay=설정.가중치_감쇠)
    로더 = 로더_만들기(X_학습, y_학습, 설정.배치_크기, 설정.씨앗)
    for 에폭 in range(1, 설정.에폭 + 1):
        한_에폭_학습(모델, 로더, 옵티마이저)
        정확도 = 평가(모델, X_검증, y_검증)[1]
        시도.report(정확도, 에폭)             # 중간 성적 알리기
        시도.set_user_attr("에폭", 에폭)
        if 시도.should_prune():               # 지금까지의 시도들 중간값보다 못하면
            raise optuna.TrialPruned()        # 여기서 그만
    return 정확도


연구 = optuna.create_study(
    study_name="옷-가지치기", storage="sqlite:///탐색.db",       # 기록을 파일에 남긴다
    direction="maximize", sampler=optuna.samplers.TPESampler(seed=0),
    pruner=optuna.pruners.MedianPruner(n_startup_trials=5, n_warmup_steps=2),
)
연구.optimize(목적함수, n_trials=40)

끝까지 = [t for t in 연구.trials if t.state == optuna.trial.TrialState.COMPLETE]
잘림 = [t for t in 연구.trials if t.state == optuna.trial.TrialState.PRUNED]
쓴_에폭 = sum(t.user_attrs["에폭"] for t in 연구.trials)
print(f"끝까지 학습 {len(끝까지)}번, 중간에 멈춤 {len(잘림)}번")
print(f"학습한 에폭 {쓴_에폭} / 가지치기가 없었다면 {len(연구.trials) * 최대_에폭}")
print(f"최고 검증 정확도 {연구.best_value:.2%} ({연구.best_trial.number + 1}번째 시도)")
print("멈춘 에폭별 개수:", {e: sum(t.user_attrs['에폭'] == e for t in 잘림) for e in range(1, 최대_에폭 + 1)})
```

```text
끝까지 학습 25번, 중간에 멈춤 15번
학습한 에폭 158 / 가지치기가 없었다면 200
최고 검증 정확도 86.64% (39번째 시도)
멈춘 에폭별 개수: {1: 0, 2: 12, 3: 3, 4: 0, 5: 0}
```

달라진 곳은 학습 루프 안의 세 줄입니다. 에폭마다 `시도.report(정확도, 에폭)`로 중간 성적을 알리고, `시도.should_prune()`이 참이면 `optuna.TrialPruned` 예외를 던져 그 시도를 끝냅니다. 판단은 `MedianPruner`가 해요. "같은 에폭에서 지금까지 시도들의 중간값보다 못하면 멈춰라"는 규칙입니다. `n_startup_trials=5`는 처음 5번은 비교할 대상이 없으니 끝까지 학습시키라는 뜻이고, `n_warmup_steps=2`는 첫 에폭 성적만 보고 섣불리 자르지 말고 2에폭부터 판단하라는 뜻이에요.

결과를 보면 40번 중 15번이 중간에 멈췄고, 대부분 2에폭에서 잘렸습니다. 학습한 에폭은 158번으로, 가지치기가 없었다면 했을 200번보다 약 21% 적어요. 그러면서 최고 검증 정확도는 86.64%로 앞의 30번 탐색(3에폭)보다 높습니다. 에폭을 5로 늘렸으니 당연한 면도 있지만, 늘어난 비용의 일부를 가지치기가 되찾아 준 거죠. 단, 처음엔 느리고 나중에 좋아지는 설정(예를 들어 학습률이 아주 작은 것)이 억울하게 잘릴 수 있다는 점은 알고 쓰세요.

### 탐색 기록 다시 열기와 중요도

`create_study`에 `storage="sqlite:///탐색.db"`를 줬기 때문에 40번의 시도가 SQLite 파일에 남아 있습니다. 탐색을 몇 시간씩 돌리다 끊겨도 기록은 그대로예요. 이 기록을 다시 열어 보겠습니다.

```python
import optuna

optuna.logging.set_verbosity(optuna.logging.WARNING)

# 앞 절에서 탐색.db에 남긴 연구를 이름으로 다시 연다 (프로그램을 껐다 켜도 그대로)
연구 = optuna.load_study(study_name="옷-가지치기", storage="sqlite:///탐색.db")
print(f"불러온 시도 {len(연구.trials)}개, 최고 {연구.best_value:.2%}")

# 시도 기록을 pandas 표로: 끝까지 학습한 것 중 위에서 다섯
표 = 연구.trials_dataframe(attrs=("number", "value", "params", "state"))
표 = 표[표.state == "COMPLETE"].sort_values("value", ascending=False).head(5)
for _, 줄 in 표.iterrows():
    print(f"{줄.number + 1:2}번째 {줄.value:.2%}  학습률 {줄.params_학습률:.5f}  드롭아웃 {줄.params_드롭아웃:.2f}  "
          f"감쇠 {줄.params_가중치_감쇠:.1e}  배치 {줄.params_배치_크기}")

# 어떤 값이 결과를 가장 많이 흔들었나
중요도 = optuna.importance.get_param_importances(연구, evaluator=optuna.importance.FanovaImportanceEvaluator(seed=0))
for 이름, 값 in 중요도.items():
    print(f"중요도 {이름}: {값:.2f}")
```

```text
불러온 시도 40개, 최고 86.64%
39번째 86.64%  학습률 0.00082  드롭아웃 0.13  감쇠 3.4e-06  배치 32
35번째 86.60%  학습률 0.00086  드롭아웃 0.15  감쇠 1.3e-06  배치 32
28번째 86.60%  학습률 0.00092  드롭아웃 0.16  감쇠 2.5e-06  배치 32
19번째 86.44%  학습률 0.00071  드롭아웃 0.18  감쇠 2.0e-06  배치 32
33번째 86.32%  학습률 0.00077  드롭아웃 0.08  감쇠 3.0e-03  배치 32
중요도 학습률: 0.67
중요도 드롭아웃: 0.17
중요도 배치_크기: 0.15
중요도 가중치_감쇠: 0.00
```

`load_study`로 이름과 저장소를 주면 연구를 그대로 되살립니다. 여기서 `optimize`를 다시 부르면 41번째 시도부터 이어서 탐색해요. 반대로 앞 예제를 처음부터 다시 실행하고 싶으면 `탐색.db`를 지우세요. 같은 이름의 연구가 이미 있으면 `create_study`가 오류를 냅니다(`load_if_exists=True`를 주면 이어 붙입니다).

`trials_dataframe`은 시도 기록을 pandas 표로 줍니다. 위에서 다섯 개를 보면 모두 학습률 0.0007~0.0009, 배치 크기 32이고, 가중치 감쇠는 0.000001부터 0.003까지 제각각이에요. 마지막 줄의 **중요도**가 이 인상을 숫자로 보여 줍니다. 결과의 흔들림 중 학습률이 0.67을 설명하고, 가중치 감쇠는 0.00으로 거의 상관이 없었어요. 다음 탐색에서는 가중치 감쇠를 빼고 학습률 범위를 좁히는 식으로 계획을 세울 수 있습니다. 이 중요도 계산(fANOVA)은 내부에서 scikit-learn의 랜덤 포레스트(3장)를 쓰기 때문에 scikit-learn이 설치되어 있어야 해요.

그런데 위의 다섯 줄을 다시 보세요. 86.64%, 86.60%, 86.60%, 86.44%, 86.32%. 1등과 2등의 차이가 0.04%p입니다. 39번째 시도가 35번째보다 정말 좋은 설정일까요? 씨앗을 바꾸면 순위가 뒤집히지 않을까요? 다음 절이 이 질문에 답합니다.

## 18.6 여러 씨앗으로 보고하기

### 6장의 86.07%를 다시 보기

6장 6.11절에서 옵티마이저를 비교할 때 Adam(lr=0.001)이 86.07%, 모멘텀을 더한 SGD가 84.12%였습니다. 그리고 "0.1~0.2%p 차이로 우열을 가리면 안 된다, 씨앗을 바꿔 여러 번 돌려 봐야 한다"고 했죠. 그 실험을 씨앗 다섯 개로 다시 해 보겠습니다. 학습률을 두 배로 키운 Adam도 함께 넣었어요.

```python
import os
import statistics

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from torchvision import datasets

데이터_폴더 = os.environ.get("BOOK_DATA_DIR", "data")

학습셋 = datasets.FashionMNIST(데이터_폴더, train=True, download=True)
시험셋 = datasets.FashionMNIST(데이터_폴더, train=False, download=True)
학습_로더 = DataLoader(TensorDataset(학습셋.data.float().unsqueeze(1) / 255, 학습셋.targets),
                    batch_size=64, shuffle=True)
X_시험, y_시험 = 시험셋.data.float().unsqueeze(1) / 255, 시험셋.targets


def 학습하고_재기(옵티마이저_만들기, 씨앗: int, 에폭수: int = 2) -> float:
    """6장 6.11절의 옵티마이저 비교와 같은 실험. 씨앗만 바꿀 수 있게 했다."""
    torch.manual_seed(씨앗)
    모델 = nn.Sequential(nn.Flatten(), nn.Linear(28 * 28, 256), nn.ReLU(),
                         nn.Linear(256, 128), nn.ReLU(), nn.Linear(128, 10))
    옵티마이저 = 옵티마이저_만들기(모델.parameters())
    for _ in range(에폭수):
        for x, y in 학습_로더:
            옵티마이저.zero_grad()
            nn.functional.cross_entropy(모델(x), y).backward()
            옵티마이저.step()
    with torch.no_grad():
        return (모델(X_시험).argmax(dim=1) == y_시험).float().mean().item()


후보 = {
    "Adam lr=0.001": lambda p: torch.optim.Adam(p, lr=0.001),
    "Adam lr=0.002": lambda p: torch.optim.Adam(p, lr=0.002),
    "SGD+momentum ": lambda p: torch.optim.SGD(p, lr=0.01, momentum=0.9),
}
씨앗들 = range(5)
결과 = {이름: [학습하고_재기(만들기, 씨앗) for 씨앗 in 씨앗들] for 이름, 만들기 in 후보.items()}

for 이름, 값들 in 결과.items():
    print(f"{이름}  " + " ".join(f"{v:.2%}" for v in 값들)
          + f"  → 평균 {statistics.mean(값들):.2%} ± {statistics.stdev(값들):.2%}")

# 같은 씨앗끼리 짝지어 차이 보기
for 상대 in ("Adam lr=0.002", "SGD+momentum "):
    차이 = [(a - b) * 100 for a, b in zip(결과["Adam lr=0.001"], 결과[상대])]     # %p 단위
    평균, 표준편차 = statistics.mean(차이), statistics.stdev(차이)
    표준오차 = 표준편차 / len(차이) ** 0.5            # 평균이 흔들리는 정도
    print(f"Adam lr=0.001 - {상대.strip()}: " + " ".join(f"{d:+.2f}" for d in 차이))
    print(f"  평균 {평균:+.2f}%p, 표준편차 {표준편차:.2f}%p, 표준오차 {표준오차:.2f}%p, "
          f"평균 ÷ 표준오차 = {평균 / 표준오차:.1f}")
```

```text
Adam lr=0.001  86.07% 85.54% 85.97% 86.41% 86.69%  → 평균 86.14% ± 0.44%
Adam lr=0.002  85.73% 85.53% 86.22% 86.28% 86.58%  → 평균 86.07% ± 0.43%
SGD+momentum   84.12% 85.02% 84.77% 84.58% 85.16%  → 평균 84.73% ± 0.41%
Adam lr=0.001 - Adam lr=0.002: +0.34 +0.01 -0.25 +0.13 +0.11
  평균 +0.07%p, 표준편차 0.21%p, 표준오차 0.10%p, 평균 ÷ 표준오차 = 0.7
Adam lr=0.001 - SGD+momentum: +1.95 +0.52 +1.20 +1.83 +1.53
  평균 +1.41%p, 표준편차 0.57%p, 표준오차 0.26%p, 평균 ÷ 표준오차 = 5.5
```

씨앗 0의 결과가 6장과 똑같이 86.07%, 84.12%입니다. 사진을 변환 없이 텐서로 바꿔 넣었을 뿐 같은 실험이라 같은 숫자가 나왔어요. 이제 씨앗 0만 봤다면 어떤 결론을 냈을지 생각해 보세요. Adam lr=0.001이 86.07%, lr=0.002가 85.73%이니 "0.001이 0.34%p 낫다"고 했을 겁니다. 그런데 씨앗 다섯 개의 평균은 86.14%와 86.07%로 0.07%p 차이뿐이고, 씨앗 2에서는 오히려 0.002가 0.25%p 높아요.

같은 설정 안에서 씨앗만 바꿔도 결과가 얼마나 흔들리는지는 **표준편차**가 알려 줍니다. 세 설정 모두 0.4%p 남짓이에요. 씨앗 하나 바꾸는 것만으로 85.54%에서 86.69%까지, 1%p 넘게 오르내립니다. 이 흔들림보다 작은 차이는 씨앗 하나짜리 실험으로는 가릴 수 없어요. `statistics`는 1권 17장에서 본 표준 라이브러리로, `mean`과 `stdev`(n - 1로 나누는 표준편차, 4장 4.10절)를 줍니다.

### 같은 씨앗끼리 짝지어 보기

두 설정을 비교할 때는 평균끼리만 보지 말고 **같은 씨앗끼리 짝지어** 차이를 보면 더 많은 것이 보입니다. 같은 씨앗이면 처음 가중치와 섞는 순서가 같아서, "운이 좋은 씨앗"의 효과가 양쪽에 똑같이 들어가거든요. 짝마다 차이를 빼면 그 운이 상쇄되고 설정의 차이만 남습니다.

출력의 마지막 네 줄이 그 계산입니다. Adam lr=0.001에서 lr=0.002를 빼면 +0.34, +0.01, -0.25, +0.13, +0.11로 부호가 오락가락해요. 평균 차이 +0.07%p를 **표준오차**(차이의 표준편차 ÷ √개수, "평균이 흔들리는 정도") 0.10%p로 나누면 0.7입니다. 평균 차이가 흔들림보다도 작다는 뜻이에요. 반대로 SGD+momentum과의 차이는 다섯 씨앗 모두 양수이고, 평균 +1.41%p를 표준오차 0.26%p로 나누면 5.5입니다. 이건 우연으로 보기 어렵죠.

이 "평균 ÷ 표준오차"가 통계에서 말하는 t 값입니다. 짝이 다섯 개일 때는 이 값이 대략 2.8을 넘으면 "우연이라고 보기 어렵다"(95% 기준)고 판단해요. 엄밀한 검정은 SciPy의 `scipy.stats.ttest_rel`이 해 주지만, 이 장에서는 다음 세 가지 습관이면 충분합니다.

- 결과는 **평균 ± 표준편차**와 씨앗 개수로 보고한다. "86.14 ± 0.44% (씨앗 5개)"처럼요.
- 두 설정을 비교할 때는 **같은 씨앗 목록**을 쓰고 짝지은 차이를 본다. 차이의 부호가 씨앗마다 바뀌면 결론을 미룬다.
- 탐색(18.5절)에서 뽑은 1등 설정은 **씨앗을 바꿔 다시 돌려** 확인한다. 수십 번 중 1등은 실력에 운이 더해진 값이라 다시 돌리면 대개 조금 내려갑니다.

> **Q. 씨앗은 몇 개면 충분한가요?**
> 정답은 없지만 흔히 3~5개로 시작합니다. 표준오차는 씨앗 수의 제곱근에 반비례해서, 씨앗을 4배로 늘려야 흔들림이 절반으로 줄어요. 그래서 "가리고 싶은 차이"가 크면 3개로도 충분하고, 0.1%p 차이를 가리려면 훨씬 많이 필요합니다. 학습 한 번이 며칠씩 걸리는 큰 모델은 씨앗을 여러 개 돌리기 어려워서, 대신 검증 데이터를 크게 잡고 차이가 큰 실험만 믿는 쪽으로 타협하기도 합니다.

## 18.7 데이터·코드·환경 버전 기록

### 데이터의 지문

설정과 씨앗이 같아도 **데이터가 바뀌면** 다른 실험입니다. 누군가 레이블 몇 개를 고쳤거나, 전처리 스크립트가 바뀌었거나, 내려받은 파일이 깨졌을 수 있어요. 데이터를 통째로 실험 폴더에 복사해 둘 수는 없으니, 18.2절에서 설정에 쓴 지문을 데이터에도 붙입니다.

```python
import hashlib
import os
from pathlib import Path

import torch

from 실험도구 import 옷_데이터


def 파일_지문(파일: Path, 조각: int = 1 << 20) -> str:
    """큰 파일도 1MB씩 읽어 가며 SHA-256 해시를 낸다."""
    해시 = hashlib.sha256()
    with 파일.open("rb") as f:
        while 덩어리 := f.read(조각):
            해시.update(덩어리)
    return 해시.hexdigest()


def 텐서_지문(*텐서들: torch.Tensor) -> str:
    """텐서 안의 숫자(와 모양)가 같으면 같은 지문."""
    해시 = hashlib.sha256()
    for t in 텐서들:
        해시.update(str(tuple(t.shape)).encode())
        해시.update(t.contiguous().numpy().tobytes())
    return 해시.hexdigest()


for 파일 in sorted(Path(os.environ.get("BOOK_DATA_DIR", "data"), "FashionMNIST", "raw").glob("*-ubyte")):
    print(f"{파일.name:28} {파일.stat().st_size:>10,}바이트  {파일_지문(파일)[:16]}")

(X_학습, y_학습), (X_검증, y_검증), _ = 옷_데이터(학습_개수=10_000)
print("학습 데이터 지문      :", 텐서_지문(X_학습, y_학습)[:16])
print("다시 나눠도           :", 텐서_지문(*옷_데이터(학습_개수=10_000)[0])[:16])
X_한점 = X_학습.clone()
X_한점[0, 0, 14, 14] += 1 / 255                     # 사진 한 장의 점 하나를 한 단계 밝게
print("점 하나만 바꿔도      :", 텐서_지문(X_한점, y_학습)[:16])
print("검증 데이터 지문      :", 텐서_지문(X_검증, y_검증)[:16])
```

```text
t10k-images-idx3-ubyte        7,840,016바이트  5b4141f0afbad91e
t10k-labels-idx1-ubyte           10,008바이트  0402a96d92fd2663
train-images-idx3-ubyte      47,040,016바이트  c59f468a2f672dc8
train-labels-idx1-ubyte          60,008바이트  bad3541b69d91243
학습 데이터 지문      : 0a802f4d1fdbc90b
다시 나눠도           : 0a802f4d1fdbc90b
점 하나만 바꿔도      : 8fe268f623ee965d
검증 데이터 지문      : 49ad3f4da16478c6
```

`파일_지문`은 큰 파일을 1MB씩 나눠 읽으며 해시를 갱신합니다. 4,700만 바이트짜리 학습 사진 파일을 한꺼번에 메모리에 올리지 않아도 돼요(`:=`는 1권 3장에서 본, 값을 대입하면서 그 값을 바로 쓰는 연산자입니다). 이 지문을 실험 기록에 함께 남겨 두면, 나중에 "같은 데이터였나?"를 지문 비교 한 번으로 확인할 수 있습니다. 공개 데이터셋은 배포하는 쪽에서 지문(체크섬)을 함께 알려 주기도 해서, 내려받은 파일이 온전한지 확인하는 데에도 씁니다.

`텐서_지문`은 파일 대신 **전처리를 마친 텐서**의 지문입니다. 원본 파일이 같아도 나누는 방법이나 정규화가 바뀌면 모델이 보는 데이터가 달라지니, 실제로 학습에 들어가는 숫자의 지문이 더 정확해요. 다시 나눠도 지문이 같고, 사진 한 장의 점 하나를 1/255만큼 밝게 했을 뿐인데 지문이 완전히 달라졌습니다. 데이터 파일 자체를 버전별로 보관하고 싶다면 git과 함께 쓰는 DVC 같은 오픈소스 도구도 있습니다.

### 코드의 버전: git 커밋

코드는 git 커밋 번호가 가장 좋은 지문입니다. 실험을 시작할 때 지금의 커밋 번호를 기록해 두면 나중에 그 시점의 코드로 정확히 돌아갈 수 있어요. 단, **커밋하지 않은 수정**이 있으면 커밋 번호만으로는 그 코드를 되살릴 수 없으니 그 여부도 함께 남깁니다. 연습용 저장소를 임시 폴더에 만들어 확인해 보겠습니다.

```python
import os
import subprocess
import tempfile
from pathlib import Path


def 코드_버전(폴더: Path) -> dict:
    """git 커밋 번호와, 커밋하지 않은 수정이 남아 있는지를 알려 준다."""
    def git(*명령) -> str:
        return subprocess.run(["git", *명령], cwd=폴더, capture_output=True, text=True,
                              check=True).stdout.strip()
    try:
        커밋 = git("rev-parse", "HEAD")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {"커밋": None, "수정됨": None}         # git 저장소가 아니거나 git이 없음
    바뀐_파일 = git("status", "--porcelain")          # 커밋 안 한 변경이 있으면 한 줄 이상
    return {"커밋": 커밋[:12], "수정됨": bool(바뀐_파일)}


# 연습용 저장소를 임시 폴더에 만들어 본다 (날짜·시간대·이름을 고정해 커밋 번호가 늘 같게)
고정 = {"GIT_AUTHOR_NAME": "책", "GIT_AUTHOR_EMAIL": "book@example.com",
        "GIT_AUTHOR_DATE": "2026-01-01T00:00:00+09:00", "GIT_COMMITTER_NAME": "책",
        "GIT_COMMITTER_EMAIL": "book@example.com", "GIT_COMMITTER_DATE": "2026-01-01T00:00:00+09:00"}
os.environ.update(고정)
with tempfile.TemporaryDirectory() as 임시:
    폴더 = Path(임시)
    print("git 저장소가 아닐 때:", 코드_버전(폴더))
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=폴더, check=True)
    (폴더 / "학습.py").write_text("학습률 = 0.001\n", encoding="utf-8")
    subprocess.run(["git", "add", "학습.py"], cwd=폴더, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "첫 실험 코드"], cwd=폴더, check=True)
    print("커밋한 직후        :", 코드_버전(폴더))
    (폴더 / "학습.py").write_text("학습률 = 0.003\n", encoding="utf-8")   # 커밋 없이 고침
    print("커밋 없이 고친 뒤  :", 코드_버전(폴더))
```

```text
git 저장소가 아닐 때: {'커밋': None, '수정됨': None}
커밋한 직후        : {'커밋': 'bc4959b5a3f4', '수정됨': False}
커밋 없이 고친 뒤  : {'커밋': 'bc4959b5a3f4', '수정됨': True}
```

`코드_버전`은 1권 17장에서 본 `subprocess`로 git 명령을 실행합니다. `git rev-parse HEAD`는 지금 커밋 번호를, `git status --porcelain`은 커밋하지 않은 변경 목록을 한 줄씩 돌려줘요. 목록이 비어 있지 않으면 "수정됨"입니다. 커밋한 직후에는 `수정됨: False`였다가, 파일을 고치자 커밋 번호는 그대로인데 `수정됨: True`가 됐습니다. 이 상태로 실험하면 "커밋 bc4959b5a3f4의 코드"라고 기록해도 실제 코드는 그와 다르다는 뜻이에요. 그래서 실험 전에 커밋하는 습관을 들이거나, 수정된 상태라면 바뀐 내용(`git diff`)까지 실험 폴더에 저장해 둡니다.

예제에서 작성자 이름과 날짜를 환경 변수로 고정한 것은 이 책의 출력과 여러분의 출력이 같게 나오도록 하기 위해서입니다. git의 커밋 번호는 내용뿐 아니라 작성자와 시각까지 넣어 계산하거든요. 날짜 끝의 `+09:00`(한국 시간)도 빼면 안 됩니다. 시간대를 적지 않으면 git이 컴퓨터에 설정된 시간대를 붙여서, 다른 시간대의 컴퓨터에서는 커밋 번호가 달라져요. 실제 프로젝트에서는 이 부분이 필요 없습니다. git 저장소가 아닌 폴더에서는 오류 대신 `None`을 돌려주게 해서, 기록 코드 때문에 학습이 멈추지 않게 했어요.

### 실행 환경

마지막은 환경입니다. 같은 코드와 데이터라도 PyTorch 버전이나 장치가 다르면 끝자리가 달라질 수 있어요(8장 8.10절).

```python
import hashlib
import importlib.metadata
import platform
import sys
from pathlib import Path

import torch


def 장치_고르기() -> torch.device:
    """쓸 수 있는 가장 빠른 장치를 고른다."""
    if torch.cuda.is_available():
        return torch.device("cuda")       # NVIDIA GPU
    if torch.backends.mps.is_available():
        return torch.device("mps")        # Apple 실리콘 GPU
    return torch.device("cpu")


def 환경_기록(패키지들: list[str], 잠금_파일: Path = Path("uv.lock")) -> dict:
    """결과에 영향을 줄 수 있는 실행 환경을 딕셔너리 하나로."""
    기록 = {
        "파이썬": platform.python_version(),
        "운영체제": f"{platform.system()} {platform.release()} ({platform.machine()})",
        "패키지": {이름: importlib.metadata.version(이름) for 이름 in 패키지들},
        "쓸 수 있는 장치": str(장치_고르기()),
        "CPU 스레드": torch.get_num_threads(),
        "CUDA": torch.version.cuda,                         # CUDA가 없는 PyTorch면 None
    }
    if 잠금_파일.exists():                                    # uv.lock이 있으면 그 지문까지
        기록["uv.lock"] = hashlib.sha256(잠금_파일.read_bytes()).hexdigest()[:16]
    return 기록


for 키, 값 in 환경_기록(["torch", "numpy", "torchvision", "optuna", "mlflow"]).items():
    print(f"{키}: {값}")
print("실행한 명령:", " ".join([Path(sys.argv[0]).name, *sys.argv[1:]]))
```

```text
파이썬: 3.12.10
운영체제: Darwin 24.6.0 (arm64)
패키지: {'torch': '2.14.1', 'numpy': '2.5.4', 'torchvision': '0.29.1', 'optuna': '5.0.0', 'mlflow': '3.17.2'}
쓸 수 있는 장치: mps
CPU 스레드: 12
CUDA: None
실행한 명령: b16_env.py
```

`platform`과 `importlib.metadata`로 파이썬·운영체제·패키지 버전을, PyTorch에게 쓸 수 있는 장치와 CPU 스레드 수, CUDA 버전을 물었습니다. 이 책의 환경은 Apple M4 Max라 장치는 `mps`, CUDA는 `None`으로 나와요. 마지막 줄은 실행한 파일 이름과 명령줄 인자라서, 여러분 화면에는 이 코드를 저장한 파일 이름이 나옵니다. CPU 스레드 수를 남기는 이유는 CPU 계산도 스레드 수에 따라 덧셈 순서가 바뀌어 끝자리가 달라질 수 있기 때문입니다.

패키지 버전을 하나하나 적는 것보다 확실한 방법은 1권 14장의 `uv.lock`입니다. 설치된 모든 패키지의 정확한 버전이 담겨 있으니, 실험할 때의 `uv.lock`을 git에 커밋해 두고 그 지문을 기록하면 환경 전체를 되살릴 수 있어요. `환경_기록`은 실행한 폴더에 `uv.lock`이 있으면 그 지문까지 남기는데, 이 예제는 `uv.lock`이 없는 폴더에서 실행해서 그 줄이 빠졌습니다.

### 재현성 보고서에 들어갈 것

지금까지 남긴 것들을 모으면 실험 하나의 **재현성 보고서**가 됩니다. 논문의 "실험 설정" 절이나 회사의 실험 보고서에 들어가는 내용이 바로 이것이에요.

| 항목 | 내용 | 출처 |
|---|---|---|
| 결과 | 지표의 평균 ± 표준편차, 씨앗 개수와 목록 | 18.6절 |
| 비교 | 기준 실험과 같은 씨앗끼리 짝지은 차이 | 18.6절 |
| 설정 | 합쳐진 최종 설정 전체(파일 + 명령줄) | 18.2절 |
| 선택 과정 | 탐색 범위와 횟수, 무엇으로 골랐나(검증), 시험은 한 번 | 18.5절 |
| 데이터 | 데이터 지문, 나누는 방법과 개수 | 18.7절 |
| 코드 | 커밋 번호와 수정 여부 | 18.7절 |
| 환경 | 파이썬·PyTorch 버전, 장치, `uv.lock` 지문 | 18.7절 |

## 18.8 실습: 작은 실험 묶음과 재현성 보고서

이 장에서 배운 것을 모두 써서, 작은 실험 묶음을 체계적으로 돌리고 보고서까지 만들어 보겠습니다. 질문은 이렇습니다. "학습 사진이 1만 장뿐일 때, 9장의 CNN에 무엇을 바꾸면 나아질까?" 6장 MLP를 비교 기준으로 함께 넣고, 실험마다 씨앗 세 개로 돌립니다.

1. 실험 목록을 YAML로 적는다: 기준 설정, 씨앗 목록, 기준에서 바꿀 값들 (18.2절)
2. 실험마다 설정 지문으로 폴더를 만들고, 설정·환경·데이터 지문·코드 지문을 남긴다 (18.2절, 18.7절)
3. 에폭별 기록은 JSON Lines로, 검증 정확도가 가장 좋았던 모델은 `best.pt`로 (18.3절, 18.4절)
4. 이미 끝난 실험은 건너뛴다. 중간에 끊겨도 다시 실행하면 남은 것만 돈다
5. 모든 폴더를 모아 평균 ± 표준편차와 짝지은 차이로 보고서를 만들고, 고른 실험만 시험 데이터로 확인한다 (18.6절)

먼저 실험을 돌립니다. 학습 1만 장, 4에폭, CPU라서 이 책의 환경에서 2분쯤 걸렸어요. 이 코드는 `Path(__file__)`로 자기 파일의 지문을 남기기 때문에, 노트북 칸에 붙여 넣지 말고 `실험도구.py`와 같은 폴더에 파일(예: `실습_실행.py`)로 저장해 `uv run python 실습_실행.py`로 실행하세요.

```python
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
```

```text
[완료] 6장 MLP
[완료] 9장 CNN
[완료] CNN + 드롭아웃 0.3
[완료] CNN + 학습률 0.003
실험 폴더 12개, 예: cnn_0c631cdec376 → ['best.pt', '결과.json', '기록.jsonl', '설정.yaml', '환경.json']
```

실험 목록이 파이썬 코드가 아니라 YAML 글자로 적혀 있다는 점을 보세요. `실험들`의 각 줄은 "기준에서 바꿀 값"만 담고 있어서, 새 실험을 추가하려면 한 줄만 더 쓰면 됩니다. 4가지 실험 × 씨앗 3개로 폴더 12개가 생겼고, 각 폴더에는 `설정.yaml`, `환경.json`, `기록.jsonl`, `best.pt`, `결과.json`이 들어 있어요. `결과.json`은 학습이 끝까지 돌았을 때만 마지막에 쓰기 때문에, 이 파일이 있는지로 "끝난 실험"을 판단합니다. 같은 코드를 다시 실행하면 12개 모두 건너뛰고, 중간에 끊겼다면 끝나지 않은 실험만 다시 돌아요.

`환경.json`의 코드 지문은 `실험도구.py`와 이 스크립트 파일의 내용을 합쳐 해시한 것입니다. git을 쓰는 프로젝트라면 18.7절의 커밋 번호를 함께 넣으면 됩니다. 이 장의 첫머리에서 본 `model_final_v2_lr0.001_진짜최종.pt` 대신, 이제 모든 모델 파일 옆에 그 모델을 만든 설정과 환경이 함께 있습니다.

이제 폴더들을 모아 보고서를 만듭니다.

```python
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
```

```text
# 재현성 보고서: FashionMNIST 작은 실험 묶음

| 실험 | 씨앗 0, 1, 2의 검증 정확도(%) | 평균 ± 표준편차 | 9장 CNN과 같은 씨앗끼리 차이(%p) |
|---|---|---|---|
| CNN + 학습률 0.003 | 87.74, 88.00, 86.28 | 87.34 ± 0.93 | +0.96, +1.44, +0.66 |
| 9장 CNN | 86.78, 86.56, 85.62 | 86.32 ± 0.62 | +0.00, +0.00, +0.00 |
| CNN + 드롭아웃 0.3 | 86.90, 86.44, 85.50 | 86.28 ± 0.71 | +0.12, -0.12, -0.12 |
| 6장 MLP | 84.52, 82.86, 83.48 | 83.62 ± 0.84 | -2.26, -3.70, -2.14 |

- 고른 실험: CNN + 학습률 0.003 (검증 평균이 가장 높음)
- 시험 정확도: 87.08 ± 0.88% (씨앗 3개)
- 공통 설정: {"모델": "cnn", "학습률": 0.003, "배치_크기": 64, "에폭": 4, "드롭아웃": 0.0, "가중치_감쇠": 0.0, "학습_개수": 10000}
- 환경: 파이썬 3.12.10, PyTorch 2.14.1, 장치 cpu
- 코드 지문 56314e6a70dd, 데이터 지문 e48b61768093, 모든 실험이 같은 환경: True
```

보고서는 마크다운 표로 만들어 `runs/실습/보고서.md`에 저장했습니다. 그대로 문서나 발표 자료에 붙일 수 있어요. 결과를 읽어 보겠습니다.

- **6장 MLP는 확실히 뒤처집니다.** 평균 83.62%로 9장 CNN보다 2.7%p 낮고, 같은 씨앗끼리 차이도 -2.26, -3.70, -2.14로 셋 다 음수예요. 9장에서 본 CNN의 장점이 학습 사진이 적을 때도 그대로입니다.
- **드롭아웃 0.3은 효과가 없었습니다.** 평균이 86.28%로 기준 86.32%와 거의 같고, 짝지은 차이가 +0.12, -0.12, -0.12로 부호가 오락가락합니다. 각 폴더의 `기록.jsonl`을 열어 보면, 9장 CNN의 4에폭째 학습 손실은 0.35~0.38, 검증 손실은 0.36~0.46으로 크게 벌어지지 않았어요. 과적합이 뚜렷해지기 전이라(8장 8.1절) 드롭아웃이 할 일이 적었던 것으로 보입니다. "효과 없음"도 기록해 둘 가치가 있는 결과입니다.
- **학습률 0.003은 나아졌습니다.** 평균 87.34%로 기준보다 1.02%p 높고, 짝지은 차이가 +0.96, +1.44, +0.66으로 셋 다 양수예요. 씨앗 세 개뿐이라 단정하기는 이르지만, 짧게 학습할 때는 조금 큰 학습률로 빨리 내려가는 쪽이 유리했다고 볼 수 있습니다.

표준편차가 0.6~0.9%p로 18.6절의 MLP 실험보다 큰 것도 눈에 띕니다. 검증 사진이 5,000장이라 시험 1만 장보다 적고, 학습 사진도 1만 장뿐이라 씨앗에 따라 더 흔들린 거예요. 실제로 CNN 세 실험에서는 모두 씨앗 2가 가장 낮습니다. 이렇게 씨앗의 운이 실험 전체에 함께 들어가기 때문에, 평균끼리 비교하는 것보다 짝지은 차이가 더 또렷한 답을 줍니다.

마지막으로 검증 평균으로 고른 "CNN + 학습률 0.003"만 시험 데이터로 확인했더니 87.08 ± 0.88%였습니다. 검증 평균 87.34%와 비슷하니, 검증으로 고른 결과를 믿을 만해요. 시험 데이터는 이렇게 **고른 다음 한 번만** 엽니다(7장 7.8절). 9장 9.5절의 같은 CNN이 91.01%를 냈던 것과 비교하면 4%p쯤 낮은데, 그때는 학습 사진 6만 장으로 5에폭을 학습했으니 이상한 일이 아니에요. 보고서의 공통 설정 줄에 학습 1만 장, 4에폭이 적혀 있으니, 이 보고서를 받은 사람도 숫자를 오해하지 않습니다. 이것이 보고서에 설정을 함께 적는 이유예요.

더 해 볼 만한 것들을 남겨 둡니다.

- 실험 목록에 `CNN + 학습률 0.003 + 드롭아웃 0.3`과 `에폭: 8`인 실험을 더해 보세요. 에폭을 늘리면 드롭아웃의 효과가 달라지는지 확인할 수 있습니다. 이미 돈 12개는 건너뛰고 새 실험만 돌 거예요.
- 18.5절의 Optuna로 CNN의 학습률과 드롭아웃을 탐색한 뒤, 찾은 설정을 이 실험 목록에 넣어 씨앗 세 개로 다시 확인해 보세요. 탐색의 1등이 다시 돌려도 1등인지 보는 것이 이 장의 핵심입니다.
- `실험_하나`에 18.4절의 MLflow 기록을 더해서, 12개 실험을 `mlflow ui`에서 곡선으로 비교해 보세요.

## 18.9 정리와 다음 장 미리보기

이 장에서 실험을 다시 할 수 있고, 많이 할 수 있고, 믿을 수 있게 만드는 습관을 익혔습니다.

- **실험의 구성 요소**: 설정, 코드, 데이터, 환경, 난수, 결과. 하나라도 빠지면 다시 할 수 없다
- **설정**: `dataclass`(`frozen=True`, `replace`, `asdict`)로 묶고, YAML에서 읽을 때는 이름과 자료형을 검사한다(`3e-4`는 글자로 읽힌다). 기본값 < 설정 파일 < 명령줄(`argparse`) 순서로 덮어쓰고, 합쳐진 최종 설정을 저장한다
- **실험 폴더**: 설정 지문(SHA-256)으로 이름을 붙여 같은 실험을 두 번 하지 않는다
- **체크포인트**: 모델·옵티마이저에 더해 스케줄러, 섞기 생성기, 전역 난수, 최고 점수까지. NumPy 난수 상태는 리스트로 바꿔 `weights_only=True`를 지킨다. 임시 파일에 쓰고 `os.replace`, `last.pt`와 `best.pt`
- **기록**: JSON Lines(덧붙이고 `flush`), TensorBoard(`SummaryWriter`, 곡선 겹쳐 보기), MLflow(파라미터·메트릭·아티팩트, `search_runs`로 표 비교)
- **탐색**: Optuna의 목적함수, `suggest_float(log=True)`, TPE가 무작위보다 좋은 곳을 더 자주 본다. `report`·`should_prune`과 `MedianPruner`로 가지치기, SQLite 저장소로 이어 가기, 중요도로 다음 탐색 계획
- **여러 씨앗**: 평균 ± 표준편차와 씨앗 개수로 보고. 같은 씨앗끼리 짝지은 차이와 표준오차로 판단. 탐색의 1등은 다시 돌려 확인
- **버전 기록**: 데이터 지문(파일·텐서), git 커밋과 수정 여부, 파이썬·패키지 버전과 장치, `uv.lock`

지금까지 우리 모델은 늘 PyTorch 안에서 학습하고 PyTorch 안에서 예측했습니다. 그런데 이 장의 실습에서 만든 `best.pt`를 휴대폰 앱이나 다른 언어로 만든 서비스에 넣으려면 어떻게 해야 할까요? 다음 19장에서는 모델을 **ONNX**라는 공통 형식으로 내보내 PyTorch 없이 실행하고, 숫자를 작은 정수로 바꿔 담는 **양자화**로 모델을 가볍고 빠르게 만듭니다. 그때도 "정확도가 얼마나 떨어졌나"를 재는 일이 핵심인데, 이 장에서 익힌 기록과 비교 습관이 그대로 쓰여요.
