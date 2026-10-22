# 부록 A. 실행 환경 만들기

새 컴퓨터에서 이 책의 예제를 처음 돌리려는 참이라고 해 봅시다. 무엇부터 설치해야 할까요? 1권에서는 파이썬과 uv만 있으면 거의 모든 예제가 돌아갔습니다. 2권은 조금 다릅니다. PyTorch는 내 컴퓨터에 어떤 그래픽 카드가 있느냐에 따라 **설치해야 하는 파일 자체가 달라지는** 라이브러리이고, Hugging Face에서 내려받는 모델은 한 개에 수백 MB에서 1GB가 넘습니다.

이 부록은 그런 준비를 한곳에 모았습니다. 장마다 Q&A 상자에 흩어 둔 설치 안내를 표 하나로 묶고, 운영체제와 그래픽 카드별로 PyTorch를 까는 방법, 설치가 제대로 됐는지 확인하는 스크립트, 자주 만나는 설치 문제, 그리고 내려받은 모델과 데이터가 어디에 쌓이는지까지 다룹니다. 처음 시작할 때 한 번 훑어보고, 문제가 생겼을 때 다시 펼쳐 보세요.

이 부록의 명령과 출력은 이 책을 쓴 컴퓨터(Apple M4 Max 맥북, macOS, 파이썬 3.12, uv 0.9.16)에서 직접 실행해 확인했습니다. 이 컴퓨터에는 NVIDIA 그래픽 카드가 없어서, NVIDIA GPU에 관한 내용은 PyTorch와 uv의 공식 설치 안내와 이 컴퓨터에서 할 수 있는 확인(설치 파일 목록 조회, 다른 운영체제용 의존성 계산)으로 적었습니다. 다만 16·17장은 RTX 4090 두 장이 달린 리눅스 서버에서 실행했고, 그때 실제로 겪은 설치 문제를 A.4절에 함께 적었어요. 2026년 10월에 확인한 내용이라, 여러분이 읽을 때는 버전 번호가 바뀌어 있을 수 있습니다.

---

## A.1 이 책에서 쓰는 패키지와 확인한 버전

2권은 장마다 필요한 패키지가 조금씩 늘어납니다. 아래 표는 각 장 첫머리의 Q&A 상자에 적은 설치 명령과, 그 장의 예제를 실행해 확인한 버전을 모은 것입니다. "더하는 패키지"는 앞 장까지 설치한 것에 **새로 더하는** 것만 적었어요.

| 장 | 더하는 패키지 | 본문에서 밝힌 버전 |
|---|---|---|
| 1장 머신러닝이란 | `numpy`, `scikit-learn` | scikit-learn 1.9 |
| 2장 데이터 준비 | `pandas` | scikit-learn 1.9, pandas 3.0 |
| 3장 고전 머신러닝 | (2장과 같음, `joblib`·`scipy`는 함께 설치됨) | scikit-learn 1.9 |
| 4장 텐서 | `torch` | PyTorch 2.14 |
| 5장 자동 미분 | (4장과 같음, 데이터는 scikit-learn 내장) | — |
| 6장 nn.Module | `torchvision` | — |
| 7장 데이터 파이프라인 | `pillow` | PyTorch 2.14, torchvision 0.29 |
| 8장 학습 잘 시키기 | `matplotlib` | — |
| 9장 CNN | (6·8장과 같음) | — |
| 10장 전이 학습 | (6장과 같음) | PyTorch 2.14.1, torchvision 0.29.1 |
| 11장 RNN·LSTM | `statsmodels` | PyTorch 2.14, statsmodels 0.15, pandas 3.0, matplotlib 3.11 |
| 12장 트랜스포머 | (4장과 같음) | PyTorch 2.14 |
| 13장 한국어 NLP | `transformers`, `datasets`, `tokenizers`, `kiwipiepy` | transformers 5.20.2, datasets 5.1.0, tokenizers 0.23.3, kiwipiepy 0.24.1, scikit-learn 1.9.1 |
| 14장 LLM과 LoRA | `peft` (`accelerate`가 함께 설치됨) | transformers 5.20.2, peft 0.21.2, accelerate 1.15.0 |
| 15장 생성 모델 | (6·8장과 같음) | torchvision 0.29.1, matplotlib 3.11.2 |
| 16장 GPU와 성능 | (6장과 같음, `torch.compile`용 `triton`은 리눅스에서 함께 설치됨) | PyTorch 2.14.1+cu126, torchvision 0.29.1, triton 3.8.0 (RTX 4090 서버) |
| 17장 분산 학습 | (6장과 같음, 통신 라이브러리 NCCL은 리눅스용 PyTorch에 들어 있음) | PyTorch 2.14.1+cu126, NCCL 2.29.3 (RTX 4090 두 장) |
| 18장 실험 관리 | `tensorboard`, `mlflow`, `optuna`, `pyyaml` | TensorBoard 2.21.0, MLflow 3.17.2, Optuna 5.0.0, PyYAML 6.0.3 |
| 19장 ONNX와 양자화 | `onnx`, `onnxscript`, `onnxruntime`, `torchao` | onnx 1.23.2, onnxscript 0.7.2, onnxruntime 1.31.0, torchao 0.18.0 |
| 20장 모델 서빙 | `fastapi[standard]`, `pytest` | FastAPI 0.156.4, Pydantic 2.14.1, uvicorn 0.54.0, python-multipart 0.0.32, Pillow 13.0.0, pytest 9.1.1 |
| 21장 종합 프로젝트 | (앞 장들과 같음, 서비스 테스트에 `httpx2`) | pandas 3.0.6, FastAPI 0.156.8, Pydantic 2.14.1, pytest 9.1.1, httpx2 2.16.0 |

모든 장은 **파이썬 3.12**에서 실행했고, PyTorch는 2.14.1입니다. "—"는 그 장 본문에 버전을 따로 적지 않았다는 뜻인데, 같은 시기에 같은 환경에서 실행했으니 바로 위아래 장과 같은 버전이라고 보면 됩니다. 다만 20·21장의 실습 서비스는 프로젝트마다 따로 만든 잠금 파일(`uv.lock`)로 설치해서, 표에 적은 FastAPI와 pytest 판이 서로 조금 다릅니다.

> **Q. 표의 버전과 똑같이 맞춰야 하나요?**
> 꼭 그럴 필요는 없습니다. 판 번호(가운데 숫자)가 같으면 예제는 거의 그대로 돌아가요. 다만 학습 결과의 소수점 아래 숫자, 경고 문구, 오류 메시지 문장은 버전에 따라 달라질 수 있습니다. 본문과 숫자를 한 자리까지 맞춰 보고 싶다면 `uv add "torch==2.14.1"`처럼 버전을 고정해서 설치하세요.

## A.2 uv로 2권 프로젝트 만들기

1권 1장에서 만든 것처럼 프로젝트 폴더 하나를 만들고 그 안에서 모든 예제를 실행하는 것이 가장 편합니다. 1권 부록 A에서 소개한 `uv init`으로 시작해 볼까요?

```bash
$ uv init pytorch-book --python 3.12
Initialized project `pytorch-book` at `.../pytorch-book`
$ cd pytorch-book
$ cat .python-version
3.12
```

`--python 3.12`를 주면 uv가 `.python-version` 파일에 3.12를 적어 두고, 이 폴더에서 `uv run`을 할 때마다 파이썬 3.12를 씁니다. 컴퓨터에 3.12가 없으면 uv가 알아서 내려받아요.

이제 2권의 중심인 PyTorch부터 넣습니다. macOS와 리눅스라면 이 한 줄이면 됩니다(윈도우에서 NVIDIA GPU를 쓰려면 A.4절을 먼저 보세요).

```bash
$ uv add torch torchvision numpy
...
 + torch==2.14.1
 + torchvision==0.29.1
 + typing-extensions==4.16.0
$ uv run python -c "import torch; print(torch.__version__)"
2.14.1
```

장을 따라가면서 필요한 패키지를 그때그때 더해도 되고, 처음부터 한꺼번에 넣어도 됩니다. 아래는 2권의 1~15장, 18~21장에서 쓰는 패키지를 모두 넣는 명령이에요. 이 책의 컴퓨터에서 실행해 보니 패키지 191개가 서로 충돌 없이 한 프로젝트에 들어갔고, 가상 환경 폴더(`.venv`)는 약 1.5GB가 됐습니다.

```bash
uv add torch torchvision numpy scikit-learn pandas matplotlib statsmodels pillow
uv add transformers datasets tokenizers kiwipiepy peft
uv add tensorboard mlflow optuna pyyaml
uv add onnx onnxscript onnxruntime torchao "fastapi[standard]"
uv add --dev pytest
```

`pytest`만 `--dev`로 넣은 이유는 1권 부록 A에서 본 그대로입니다. 테스트 도구는 개발할 때만 필요하고, 완성한 프로그램을 배포할 때는 필요 없으니까요. 20장에서 Docker 이미지를 만들 때 이 구분이 실제로 쓰입니다.

> **Q. 이미 1권 프로젝트가 있는데 거기에 더해도 되나요?**
> 됩니다. 다만 2권 패키지는 크기가 커서(위 명령 전체로 약 1.5GB), 1권 프로젝트와 폴더를 나눠 두는 편이 정리하기 쉽습니다. 프로젝트를 지우고 싶을 때 폴더째 지우면 가상 환경까지 함께 사라지는 것도 uv 프로젝트의 장점이에요.

## A.3 macOS: Apple 실리콘과 MPS

맥이라면 설치는 가장 간단합니다. `uv add torch`가 설치하는 PyTorch에 Apple 실리콘(M1~M4 등)의 GPU를 쓰는 **MPS(Metal Performance Shaders)** 기능이 이미 들어 있거든요. 따로 드라이버나 도구를 설치할 필요가 없습니다. 이 책의 예제도 대부분 이 방식으로, 맥북 한 대에서 실행했어요.

조건이 두 가지 있습니다. PyTorch 2.14.1의 맥용 설치 파일은 이름이 `macosx_14_0_arm64`로 끝나는 것 하나뿐이에요. 즉 **Apple 실리콘 맥**이어야 하고, **macOS 14(Sonoma) 이상**이어야 합니다. 이 책의 컴퓨터에서 인텔 맥(x86_64)을 대상으로 설치할 버전을 계산하게 해 봤더니, uv는 인텔 맥용 파일이 있는 마지막 버전인 **2.2.2**를 골랐습니다. 2.2.2는 이 책의 예제가 쓰는 기능 일부가 없는 오래된 버전이라, 인텔 맥이라면 A.5절의 Colab을 쓰는 편이 낫습니다.

MPS는 거의 모든 예제에서 잘 동작하지만, CUDA와 다른 점이 몇 가지 있습니다.

- **64비트 실수(float64)를 쓸 수 없습니다.** 아래 A.7절에서 실제 오류를 보여 드립니다.
- 아직 MPS에서 지원하지 않는 연산을 만나면 오류가 납니다. 이때 환경 변수 `PYTORCH_ENABLE_MPS_FALLBACK=1`을 주면 그 연산만 CPU에서 계산하도록 할 수 있어요(PyTorch 공식 문서의 MPS 환경 변수 목록). 대신 그 부분은 느려집니다.
- 같은 코드라도 CPU와 결과가 소수점 아래에서 조금씩 다를 수 있습니다. 그래서 이 책에서 정확한 숫자를 인용하는 작은 학습 예제는 대부분 CPU에서 돌렸고, MPS로 돌린 예제에는 그렇다고 밝혀 두었어요.

```bash
# MPS에서 지원하지 않는 연산을 CPU로 돌려서 계산하게 하기 (macOS·리눅스 셸)
PYTORCH_ENABLE_MPS_FALLBACK=1 uv run python 학습.py
```

## A.4 리눅스·윈도우와 NVIDIA GPU: CUDA

NVIDIA 그래픽 카드가 있는 컴퓨터라면 이야기가 조금 복잡해집니다. PyTorch는 NVIDIA의 계산 도구인 **CUDA**의 버전별로 설치 파일을 따로 만들고, 운영체제마다 기본으로 설치되는 파일도 다르기 때문이에요. 순서대로 보겠습니다.

### 먼저 그래픽 카드 드라이버

CUDA로 계산하려면 NVIDIA 그래픽 카드 드라이버가 설치되어 있어야 합니다. 드라이버가 설치되어 있으면 터미널에서 `nvidia-smi` 명령이 그래픽 카드 이름과 드라이버 버전, 그 드라이버가 지원하는 CUDA 버전을 보여 줍니다. 이 명령이 없다고 나오면 NVIDIA 홈페이지에서 그래픽 카드에 맞는 드라이버부터 설치하세요. PyTorch 설치 파일에는 CUDA 계산에 필요한 라이브러리가 함께 들어 있어서, **CUDA 개발 도구(CUDA Toolkit)를 따로 설치할 필요는 없습니다.** 필요한 것은 드라이버뿐이에요.

### 기본 설치는 무엇을 깔까요?

uv 공식 문서의 PyTorch 안내에 따르면, 아무 설정 없이 `uv add torch`를 하면 PyPI(파이썬 패키지 공용 저장소)에서 설치하는데, PyPI의 PyTorch는 **리눅스에서는 GPU(CUDA)용, 윈도우와 macOS에서는 CUDA가 빠진 빌드**입니다(macOS 빌드에는 A.3절의 MPS가 들어 있어요). 이 책의 컴퓨터에서 운영체제별로 PyTorch 2.14.1이 함께 끌어오는 패키지를 계산해 봤더니 정말 그랬어요.

```bash
$ uv pip compile req.in --python-version 3.12 --python-platform x86_64-unknown-linux-gnu
...
nvidia-cuda-runtime==13.0.96
nvidia-cudnn-cu13==9.24.0.43
...
torch==2.14.1
triton==3.8.0
$ uv pip compile req.in --python-version 3.12 --python-platform x86_64-pc-windows-msvc
...
torch==2.14.1
```

`req.in`에는 `torch==2.14.1` 한 줄만 적었습니다. 리눅스용 결과에는 `nvidia-`로 시작하는 CUDA 13 라이브러리가 줄줄이 따라오고, 윈도우용 결과에는 하나도 없어요. 정리하면 이렇습니다.

| 운영체제 | `uv add torch`로 설치되는 것 | NVIDIA GPU를 쓰려면 |
|---|---|---|
| 리눅스 | CUDA 13용 PyTorch | 드라이버가 CUDA 13을 지원하면 그대로 사용 |
| 윈도우 | CPU 전용 PyTorch | PyTorch 인덱스를 지정해서 다시 설치 (아래) |
| macOS | MPS가 들어 있는 PyTorch | 해당 없음(맥용 CUDA 빌드는 없음) |

### PyTorch 인덱스 지정하기

윈도우에서 GPU를 쓰려면, 또는 리눅스에서 드라이버가 오래되어 더 낮은 CUDA 버전이 필요하면, PyTorch가 직접 운영하는 설치 파일 저장소(**인덱스**)를 지정합니다. 주소는 `https://download.pytorch.org/whl/` 뒤에 CUDA 버전을 붙인 꼴이에요. `cu126`은 CUDA 12.6, `cu130`은 CUDA 13.0이라는 뜻입니다.

어떤 CUDA 버전용 파일이 있는지는 PyTorch 버전마다 다릅니다. 2026년 10월에 이 인덱스들을 직접 조회해 보니 PyTorch 2.14.1은 `cpu`, `cu126`, `cu130`, `cu132`에 리눅스용과 윈도우용 파일이 있었고, `cu128`에는 없었어요. 여러분이 설치할 때는 PyTorch 홈페이지의 설치 안내(Get Started) 페이지에서 운영체제, 패키지 도구, CUDA 버전을 고르면 나오는 명령을 기준으로 삼으세요.

uv 프로젝트에서는 `pyproject.toml`에 인덱스를 적어 둡니다. 아래는 uv 공식 문서의 예를 CUDA 13.0으로 바꾼 것이에요.

```toml
[[tool.uv.index]]
name = "pytorch-cu130"
url = "https://download.pytorch.org/whl/cu130"
explicit = true

[tool.uv.sources]
torch = [
  { index = "pytorch-cu130", marker = "sys_platform == 'linux' or sys_platform == 'win32'" },
]
torchvision = [
  { index = "pytorch-cu130", marker = "sys_platform == 'linux' or sys_platform == 'win32'" },
]
```

설정이 두 부분으로 나뉘어 있죠?

- `[[tool.uv.index]]`는 "이런 이름의 저장소가 있다"고 알려 줍니다. `explicit = true`는 **이 저장소를 지정한 패키지에만 쓰라**는 뜻이에요. 이 줄이 없으면 numpy나 pandas까지 이 저장소에서 찾으려 할 수 있습니다.
- `[tool.uv.sources]`는 `torch`와 `torchvision`을 그 저장소에서 가져오라고 정합니다. `marker`의 조건 덕분에 리눅스와 윈도우에서만 이 저장소를 쓰고, 맥에서는 PyPI의 MPS용 PyTorch를 그대로 씁니다.

이렇게 적은 뒤 `uv add torch torchvision`(이미 넣었다면 `uv lock`)을 실행하면 됩니다. 이 책의 컴퓨터에서 이 설정으로 잠금 파일을 만들어 보니, `uv.lock`에 맥용 `torch 2.14.1`(PyPI)과 리눅스·윈도우용 `torch 2.14.1+cu130`(PyTorch 인덱스)이 함께 기록됐어요. 잠금 파일 하나로 세 운영체제를 모두 챙기는 셈입니다. 16·17장을 실행한 리눅스 서버에서는 이 `cu130` 빌드가 바로 돌지 않았습니다. 서버의 드라이버(550 버전)가 CUDA 12.4까지만 지원해서 `NVIDIA driver on your system is too old` 오류가 났거든요. 그래서 위 설정의 `cu130`을 모두 `cu126`으로 바꿔 `torch 2.14.1+cu126`을 설치했고, 이 빌드로 두 GPU 모두에서 학습이 돌았습니다. `nvidia-smi`가 보여 주는 CUDA 버전보다 높은 빌드를 깔면 이렇게 되니, 드라이버를 올릴 수 없는 서버라면 그보다 낮거나 가까운 버전의 인덱스를 고르세요.

### pip을 쓰는 환경이라면

Colab이나 회사 서버처럼 uv 프로젝트가 아닌 곳에서는 PyTorch 설치 안내 페이지의 pip 명령을 씁니다. 그 페이지가 보여 주는 명령은 이런 꼴이에요.

```bash
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu130
```

uv에는 이 고르기를 대신해 주는 기능도 있습니다. `uv pip install --torch-backend=auto torch`는 설치된 NVIDIA 드라이버(AMD·인텔 GPU도)를 조사해서 가장 잘 맞는 PyTorch 인덱스를 고르고, 맞는 GPU가 없으면 CPU 전용 인덱스를 씁니다(uv 공식 문서). 이 책의 uv 0.9.16에도 이 옵션이 있었고, 맥에서 시험 삼아 실행하니 PyPI의 `torch==2.14.1`을 골랐어요. 이 기능은 `uv add`가 아니라 `uv pip` 명령에서만 쓸 수 있습니다.

> **Q. 설치한 PyTorch가 GPU용인지 어떻게 아나요?**
> PyTorch 인덱스에서 받은 파일은 버전 뒤에 `+cu130`, `+cpu`처럼 꼬리표가 붙습니다(설치 파일 이름이 `torch-2.14.1+cu130-...`). 파이썬 안에서는 `torch.version.cuda`를 보세요. CPU 전용이나 맥용 빌드는 `None`이고, CUDA용 빌드는 CUDA 버전 문자열이 나옵니다. 그다음 `torch.cuda.is_available()`이 `True`인지 확인하면 드라이버까지 연결된 것입니다. A.6절의 스크립트가 이 두 가지를 함께 출력해요.

## A.5 GPU가 없을 때: Colab과 클라우드 GPU

GPU가 없어도 이 책은 따라갈 수 있습니다. 4장 Q&A에서 말했듯 예제를 노트북 CPU나 맥의 MPS에서 몇 분 안에 끝나도록 크기를 맞췄거든요. 그래도 15장 확산 모델이나 13·14장의 미세조정처럼 계산이 많은 예제를 빠르게 돌리고 싶다면 GPU를 빌려 쓰는 방법이 있습니다.

가장 쉬운 방법은 1권 1장의 "설치가 어렵다면: Colab에서 시작하기"에서 만난 **Google Colab**입니다. Colab은 인터넷 너머의 컴퓨터를 빌려 쓰는 서비스라, 메뉴에서 런타임 유형을 GPU로 바꾸면 NVIDIA GPU가 달린 컴퓨터를 쓸 수 있어요. 무료 사용량에는 한도가 있고, 어떤 GPU를 얼마나 오래 쓸 수 있는지는 구글이 수시로 바꾸니 그때그때 Colab 안내를 확인하세요. Colab에는 PyTorch가 대개 미리 설치되어 있어서 `import torch`부터 바로 시작할 수 있고, 없는 패키지는 노트북 칸에 `!pip install 패키지`로 넣습니다.

Colab을 쓸 때 기억할 점이 세 가지 있습니다.

- 빌린 컴퓨터는 한동안 쓰지 않으면 **반납되고, 그 안의 파일도 함께 사라집니다.** 학습한 모델(`.pt` 파일)은 구글 드라이브에 저장하세요.
- 장치를 고르는 코드는 바꿀 필요가 없습니다. 아래 A.6절의 `장치_고르기()`가 Colab에서는 `cuda`를 고릅니다.
- Colab의 PyTorch 버전은 이 책의 버전과 다를 수 있습니다. 첫 칸에서 `torch.__version__`을 확인해 두세요.

Colab보다 오래, 크게 쓰려면 클라우드 회사(AWS, Google Cloud, Azure 등)나 GPU 대여 전문 서비스에서 GPU 서버를 시간 단위로 빌릴 수 있습니다. 서비스마다 화면과 요금이 달라서 이 책에서 따라 하기를 싣지는 않았지만, 일반적으로 지킬 점은 같아요.

- **쓰지 않을 때는 반드시 꺼 두세요.** 대부분 켜져 있는 시간만큼 요금이 나갑니다.
- 빌린 서버는 대개 리눅스입니다. A.4절의 리눅스 설치가 그대로 적용되고, 서버에 드라이버가 미리 설치된 이미지를 고르면 `nvidia-smi`부터 바로 됩니다.
- 코드와 데이터는 git이나 클라우드 저장소로 옮기고, 결과는 끄기 전에 내려받으세요. 18장의 실험 기록 습관이 이때 빛을 봅니다.

## A.6 장치 고르기와 설치 확인 스크립트

### 장치_고르기() 다시 보기

4장 4.8절에서 만든 함수를 다시 한번 보겠습니다. 이 책의 거의 모든 장이 이 함수를 그대로 씁니다.

```python
def 장치_고르기() -> torch.device:
    """쓸 수 있는 가장 빠른 장치를 고른다."""
    if torch.cuda.is_available():
        return torch.device("cuda")       # NVIDIA GPU
    if torch.backends.mps.is_available():
        return torch.device("mps")        # Apple 실리콘 GPU
    return torch.device("cpu")
```

확인하는 순서가 곧 우선순위입니다. NVIDIA GPU가 있으면 `cuda`, 없고 Apple 실리콘이면 `mps`, 둘 다 없으면 `cpu`예요. 이 함수 덕분에 같은 코드가 맥, 윈도우, 리눅스, Colab 어디서나 고칠 곳 없이 돌아갑니다. 쓰는 법은 6장 6.9절에서 본 세 단계 그대로입니다.

```python
import torch
from torch import nn


def 장치_고르기() -> torch.device:
    """쓸 수 있는 가장 빠른 장치를 고른다."""
    if torch.cuda.is_available():
        return torch.device("cuda")       # NVIDIA GPU
    if torch.backends.mps.is_available():
        return torch.device("mps")        # Apple 실리콘 GPU
    return torch.device("cpu")


장치 = 장치_고르기()
torch.manual_seed(0)
모델 = nn.Linear(4, 2).to(장치)            # 1) 모델을 장치로 (6장 6.9절)
x = torch.randn(8, 4).to(장치)              # 2) 데이터도 같은 장치로
출력 = 모델(x)
print(출력.device, tuple(출력.shape))
print(출력.argmax(dim=1).cpu().tolist())    # 3) 출력은 CPU로 꺼내서 파이썬 값으로
```

```text
mps:0 (8, 2)
[1, 0, 0, 1, 1, 0, 0, 1]
```

모델과 데이터를 같은 장치로 옮기고, 결과를 파이썬 값으로 쓸 때는 `.cpu()`로 꺼냅니다. 이 컴퓨터에서는 `mps:0`, 즉 첫 번째 MPS 장치에서 계산됐어요. 셋 중 하나라도 빠뜨리면 4장 4.8절에서 본 "같은 장치에 있어야 한다"는 오류를 만납니다.

### 설치 확인 스크립트

새 컴퓨터에 환경을 만들었거나 Colab에 처음 접속했다면 아래 스크립트부터 실행해 보세요. 파이썬과 PyTorch 버전, CUDA·MPS를 쓸 수 있는지, 고른 장치에서 실제로 계산이 되는지를 한 번에 봅니다. `설치_확인.py`로 저장하고 `uv run python 설치_확인.py`로 실행하면 됩니다.

```python
# 설치_확인.py: 새 컴퓨터에서 가장 먼저 실행해 보는 점검 스크립트
import platform
import sys

import torch


def 장치_고르기() -> torch.device:
    """쓸 수 있는 가장 빠른 장치를 고른다."""
    if torch.cuda.is_available():
        return torch.device("cuda")       # NVIDIA GPU
    if torch.backends.mps.is_available():
        return torch.device("mps")        # Apple 실리콘 GPU
    return torch.device("cpu")


print("파이썬     :", sys.version.split()[0])
print("운영체제   :", platform.system(), platform.machine())
print("PyTorch    :", torch.__version__)
print("CUDA 빌드  :", torch.version.cuda)            # CPU·MPS용 빌드면 None
print("CUDA 사용  :", torch.cuda.is_available())
if torch.cuda.is_available():
    print("GPU 이름   :", torch.cuda.get_device_name(0))
print("MPS 사용   :", torch.backends.mps.is_available())

장치 = 장치_고르기()
print("고른 장치  :", 장치)

# 같은 계산을 CPU와 고른 장치에서 해 보고 결과를 비교한다
torch.manual_seed(0)
a = torch.randn(512, 512)
b = torch.randn(512, 512)
cpu_결과 = a @ b
장치_결과 = (a.to(장치) @ b.to(장치)).cpu()
print("행렬 곱 모양:", tuple(장치_결과.shape))
print("CPU와 같은가:", torch.allclose(cpu_결과, 장치_결과, atol=1e-3))
```

이 책의 컴퓨터에서 실행한 결과입니다.

```text
파이썬     : 3.12.10
운영체제   : Darwin arm64
PyTorch    : 2.14.1
CUDA 빌드  : None
CUDA 사용  : False
MPS 사용   : True
고른 장치  : mps
행렬 곱 모양: (512, 512)
CPU와 같은가: True
```

읽는 법은 이렇습니다.

- **CUDA 빌드**가 `None`이면 설치된 PyTorch에 CUDA 기능이 아예 없다는 뜻입니다. 맥에서는 정상이에요. NVIDIA GPU가 있는 윈도우 컴퓨터에서 `None`이 나오면 CPU 전용 PyTorch가 설치된 것이니 A.4절대로 다시 설치하세요.
- **CUDA 빌드**에 버전이 나오는데 **CUDA 사용**이 `False`라면 PyTorch는 맞게 설치됐지만 드라이버와 연결되지 않은 경우입니다. `nvidia-smi`가 되는지, 드라이버가 그 CUDA 버전을 지원하는지 확인하세요.
- 마지막 두 줄은 실제로 그 장치에서 행렬 곱을 하고 CPU 결과와 비교한 것입니다. GPU는 계산 순서가 달라 소수점 아래 끝자리가 조금 다를 수 있어서 `allclose`에 여유(`atol=1e-3`)를 줬어요. `True`면 그 장치로 학습할 준비가 된 것입니다.

NVIDIA GPU가 있는 컴퓨터라면 `GPU 이름` 줄이 하나 더 나오고 `고른 장치`가 `cuda`가 될 것입니다. 이 책의 컴퓨터에서는 확인할 수 없었던 출력이라 결과를 싣지 않았어요.

## A.7 자주 만나는 설치 문제

설치하다 막히는 지점은 대개 정해져 있습니다. 이 책의 컴퓨터에서 직접 재현해 본 것만 모았어요.

### 파이썬 버전이 맞지 않을 때

PyTorch 2.14.1은 파이썬 3.10부터 3.14까지만 설치 파일을 냅니다. 파이썬 3.9 환경에서 설치하려고 하면 uv가 이렇게 알려 줘요.

```text
hint: You require CPython 3.9 (`cp39`), but we only found wheels
for `torch` (v2.14.1) with the following Python implementation tags:
`cp310`, `cp311`, `cp312`, `cp313`, `cp314`
```

"`cp39`가 필요한데 `cp310`~`cp314`용 파일만 찾았다"는 뜻입니다. `cp312`가 CPython 3.12라는 뜻이에요. 해결은 간단합니다. 프로젝트의 파이썬을 바꾸면 돼요(`uv python pin 3.12`). 1권 부록 A에서 본 대로 uv가 3.12를 알아서 내려받습니다.

### 운영체제용 설치 파일이 없을 때

같은 종류의 오류가 운영체제 때문에 나기도 합니다. A.3절에서 본 인텔 맥이나 macOS 13 이하에서 `torch==2.14.1`을 설치하려 하면 "이 플랫폼용 파일만 있다"는 안내가 나와요.

```text
hint: Wheels are available for `torch` (v2.14.1) on the following
platforms: `manylinux_2_28_aarch64`, `manylinux_2_28_x86_64`,
`macosx_14_0_arm64`, `win_amd64`
```

목록이 곧 설치할 수 있는 곳입니다. 리눅스(인텔·AMD 계열 `x86_64`와 ARM 계열 `aarch64`), macOS 14 이상의 Apple 실리콘, 64비트 윈도우예요. 여기에 없는 컴퓨터라면 버전을 고정하지 않았을 때 uv가 설치할 수 있는 옛 버전을 고르는데, 그러면 이 책의 예제가 돌지 않을 수 있습니다. 이럴 때는 A.5절의 Colab이 가장 빠른 해결책이에요.

### GPU가 있는데 CUDA가 False일 때

NVIDIA GPU가 달린 윈도우 컴퓨터에서 `uv add torch`만 했다면, A.4절에서 본 대로 CPU 전용 PyTorch가 설치되어 있습니다. A.6절 스크립트의 `CUDA 빌드`가 `None`으로 나오는 것으로 확인할 수 있어요. `pyproject.toml`에 PyTorch 인덱스를 적고 다시 설치하세요. `CUDA 빌드`에 버전이 나오는데도 `False`라면 드라이버 문제입니다.

### MPS에서 float64 오류

맥에서 가장 자주 만나는 오류입니다. NumPy 배열의 기본 실수 자료형은 float64인데, 이걸 `torch.from_numpy`로 바꾸면 자료형이 그대로 따라오고, MPS는 float64를 지원하지 않아요.

```python
import numpy as np
import torch

배열 = np.array([0.1, 0.2, 0.3])             # NumPy의 기본 실수 자료형은 float64
t = torch.from_numpy(배열)
print("자료형:", t.dtype)

if torch.backends.mps.is_available():
    try:
        t.to("mps")
    except TypeError as 오류:
        print("오류:", 오류)
    print("고친 뒤:", t.float().to("mps").dtype)  # float32로 바꾼 다음 옮긴다
```

```text
자료형: torch.float64
오류: Cannot convert a MPS Tensor to float64 dtype as the MPS framework doesn't support float64. Please use float32 instead.
고친 뒤: torch.float32
```

오류 문장이 해결책까지 알려 줍니다. "float32를 쓰라"죠. `.float()`로 float32로 바꾼 뒤 옮기면 됩니다. `.float()`는 4장 4.3절에서 본 `.to(torch.float32)`를 줄여 쓴 것이에요. pandas에서 꺼낸 값, scikit-learn 데이터셋도 대개 float64이니 텐서로 만들 때 `dtype=torch.float32`를 붙이는 습관을 들이면 이 오류를 만나지 않아요.

### NumPy 없이 PyTorch만 설치했을 때

PyTorch는 NumPy 없이도 설치되고 대부분 동작합니다. 그런데 `.numpy()`처럼 NumPy와 주고받는 기능을 쓰는 순간 오류가 나요. 이 책의 컴퓨터에서 `uv run --with torch`로 NumPy 없는 환경을 만들어 `torch.ones(2).numpy()`를 실행했더니 이렇게 나왔습니다.

```text
RuntimeError: Numpy is not available
```

사실 신호는 그 전에 이미 옵니다. NumPy가 없는 환경에서는 `import torch`를 할 때 `UserWarning: Failed to initialize NumPy: No module named 'numpy'`라는 경고가 먼저 찍혀요. 경고라서 지나치기 쉬운데, 이 문장을 봤다면 NumPy가 빠진 것입니다.

`uv add numpy`로 해결됩니다. A.2절의 명령처럼 처음부터 `torch`와 `numpy`를 함께 넣어 두면 만날 일이 없어요.

### 장치가 섞였을 때

설치 문제는 아니지만 처음 GPU를 쓸 때 가장 많이 만나는 오류라 함께 적어 둡니다. 4장 4.8절에서 본 `Expected all tensors to be on the same device`예요. 모델과 데이터, 그리고 손실 계산에 들어가는 정답 텐서까지 모두 같은 장치에 있어야 합니다. A.6절의 세 단계(모델 옮기기, 데이터 옮기기, 결과 꺼내기)를 확인하세요.

## A.8 내려받은 모델은 어디에 쌓일까: 캐시와 디스크 용량

### Hugging Face 캐시와 HF_HOME

13·14·20장에서 `from_pretrained("klue/bert-base")`처럼 모델을 불러오면, 처음 한 번만 인터넷에서 내려받고 그다음부터는 컴퓨터에 저장해 둔 것을 씁니다. 이렇게 다시 쓰려고 저장해 두는 곳을 **캐시(cache)** 라고 해요. 10장의 torchvision 사전학습 가중치도 마찬가지로 캐시에 저장됩니다. 지금 내 컴퓨터의 캐시 위치는 이렇게 확인할 수 있어요.

```python
import os
from pathlib import Path

import torch
from huggingface_hub import constants


def 짧게(경로: str | Path) -> str:
    """사용자 폴더 부분을 ~로 줄여서 보여 준다."""
    return str(경로).replace(str(Path.home()), "~")


print("HF_HOME 지정  :", os.environ.get("HF_HOME", "(지정 안 함)"))
print("Hugging Face  :", 짧게(constants.HF_HOME))
print("  모델 캐시   :", 짧게(constants.HF_HUB_CACHE))
print("torchvision   :", 짧게(torch.hub.get_dir()))
print("데이터 폴더   :", os.environ.get("BOOK_DATA_DIR", "data"))
```

```text
HF_HOME 지정  : (지정 안 함)
Hugging Face  : ~/.cache/huggingface
  모델 캐시   : ~/.cache/huggingface/hub
torchvision   : ~/.cache/torch/hub
데이터 폴더   : data
```

아무것도 지정하지 않으면 Hugging Face는 사용자 폴더의 `.cache/huggingface`를, torchvision은 `.cache/torch`를 씁니다. 모델 파일은 그 안의 `hub` 폴더에 들어가요. 위치를 바꾸고 싶으면 환경 변수 **`HF_HOME`** 을 지정합니다. 사용자 폴더가 있는 디스크가 작아서 외장 디스크에 두고 싶을 때 유용해요(torchvision 쪽은 환경 변수 `TORCH_HOME`이 같은 역할을 합니다).

```bash
# macOS·리눅스: 이번 실행에만 적용
HF_HOME=/Volumes/외장/hf uv run python 미세조정.py
```

```powershell
# 윈도우 PowerShell: 이 창에서만 적용
$env:HF_HOME = "D:\hf"
uv run python 미세조정.py
```

계속 쓰려면 셸 설정 파일(macOS의 `~/.zshrc` 등)이나 윈도우의 환경 변수 설정에 넣어 두세요. 1권 19장과 2권 20장에서처럼, 설정은 코드에 박지 않고 환경 변수로 바꾸는 것이 원칙입니다.

### 얼마나 차지할까

이 책을 쓰면서 1~15장, 18~21장의 예제를 모두 실행하고 나니 캐시와 데이터 폴더가 이만큼 쌓였습니다. Hugging Face 모델은 `hf cache ls` 명령(아래)으로, 나머지는 폴더 크기를 재서 적었어요.

| 무엇 | 쓰는 장 | 크기 |
|---|---|---|
| Qwen2.5-0.5B-Instruct (언어 모델) | 14·20장 | 약 1,000MB |
| klue/bert-base (한국어 BERT) | 13장 | 약 446MB |
| xlm-roberta-base, bert-base-multilingual-cased (토크나이저만) | 13장 | 약 17MB |
| KLUE 데이터셋 (뉴스 제목 주제 분류) | 13장 | 약 5MB(내려받은 파일) + 15MB(변환본) |
| torchvision 사전학습 가중치 (ResNet18, MobileNetV3-Small, EfficientNet-B0) | 10장 | 45MB + 9.8MB + 20MB |
| EuroSAT 위성 사진 (압축 파일과 푼 파일) | 10장 | 약 223MB |
| FashionMNIST | 6·9·15·18~20장 | 약 82MB |
| NSMC 네이버 영화 리뷰 | 13장 | 약 19MB |
| 가상 환경 `.venv` (A.2절의 패키지 전체) | 전체 | 약 1.5GB |

모두 합치면 4GB 가까이 됩니다. 여기에 장마다 저장하는 체크포인트와 13장에서 미세조정한 모델(이 책의 컴퓨터에서 약 420MB)이 더해지니, **여유 공간을 10GB쯤 확보해 두면** 넉넉해요.

Hugging Face 캐시에 무엇이 있는지는 `huggingface_hub`에 들어 있는 `hf` 명령으로 볼 수 있습니다. `transformers`를 설치하면 함께 설치돼요. 이 책의 캐시를 조회한 결과입니다.

```bash
$ uv run hf cache ls
id	size	last_accessed	last_modified	refs
dataset/klue/klue	5.0M	4 hours ago	4 hours ago	['main']
model/FacebookAI/xlm-roberta-base	14.2M	4 hours ago	4 hours ago	['main']
model/Qwen/Qwen2.5-0.5B-Instruct	999.6M	2 hours ago	4 hours ago	['main']
model/google-bert/bert-base-multilingual-cased	3.0M	4 hours ago	4 hours ago	['main']
model/klue/bert-base	445.7M	3 hours ago	4 hours ago	['main']

Found 5 repo(s) for a total of 5 revision(s) and 1.5G on disk.
```

다 본 모델은 `hf cache rm model/Qwen/Qwen2.5-0.5B-Instruct`처럼 지울 수 있습니다. 지워도 다음에 필요하면 다시 내려받을 뿐이니 걱정하지 않아도 돼요. torchvision 가중치와 데이터 폴더는 그냥 파일이라 폴더째 지우면 됩니다.

## A.9 데이터 폴더 관례: BOOK_DATA_DIR

이 책의 예제는 인터넷에서 받는 데이터셋을 현재 폴더 아래 `data/`에 저장합니다. 6장의 `datasets.FashionMNIST("data", ...)`처럼요. 그런데 장마다 폴더를 따로 만들어 예제를 실행하면 같은 FashionMNIST를 장마다 다시 받게 됩니다. 그래서 2·3·12장의 예제는 데이터 폴더를 환경 변수 **`BOOK_DATA_DIR`** 로 바꿀 수 있게 썼어요. 규칙은 하나뿐입니다. "`BOOK_DATA_DIR`이 있으면 그 폴더, 없으면 `data`."

```python
import os
from pathlib import Path


def 데이터_폴더() -> Path:
    """예제 데이터를 둘 폴더. BOOK_DATA_DIR이 있으면 그곳, 없으면 ./data"""
    return Path(os.environ.get("BOOK_DATA_DIR", "data"))


os.environ.pop("BOOK_DATA_DIR", None)            # 지정하지 않았을 때
print(데이터_폴더())
os.environ["BOOK_DATA_DIR"] = "/Volumes/외장/책데이터"  # 지정했을 때 (예)
print(데이터_폴더())
print(데이터_폴더() / "FashionMNIST")
```

```text
data
/Volumes/외장/책데이터
/Volumes/외장/책데이터/FashionMNIST
```

`os.environ.get(이름, 기본값)`은 1권 17장에서 본 그대로, 환경 변수가 없으면 기본값을 돌려줍니다. 지정하지 않으면 상대 경로 `data`이니 지금 실행하는 폴더 아래에, 지정하면 그 폴더에 데이터가 모여요. 다른 장의 예제도 `"data"`라고 적힌 자리를 `데이터_폴더()`로 바꾸면 모든 장이 한 폴더를 같이 쓰게 됩니다.

```bash
# 모든 장의 예제가 같은 데이터 폴더를 쓰게 하기 (macOS·리눅스)
export BOOK_DATA_DIR="$HOME/book-data"
uv run python 06_옷분류.py
```

정리하면, 이 책의 예제가 컴퓨터에 남기는 것은 세 곳입니다. 패키지는 프로젝트의 `.venv`, 모델은 `HF_HOME`과 torchvision 캐시, 데이터는 `BOOK_DATA_DIR`(기본 `data/`)이에요. 디스크가 부족하거나 컴퓨터를 옮길 때 이 세 곳만 기억하면 됩니다.
