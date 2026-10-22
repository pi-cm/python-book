# 파이썬 완전 백과사전 2권(PyTorch 딥러닝 편) — 예제 코드

책에 실린 코드 블록을 장 폴더에 블록 하나당 파일 하나로 모았습니다.
파일 맨 위 주석에 원고의 장·절과 줄 번호가 있어 책의 어느 부분인지 바로 찾을 수 있어요.
이 파일들은 원고를 쓸 때 실제로 실행해 책의 출력을 만든 바로 그 코드입니다.

## 준비

[uv](https://docs.astral.sh/uv/)가 설치되어 있으면 이 폴더에서 한 번만 실행합니다.

```bash
uv sync          # 파이썬 3.12와 PyTorch 2.14.1 등 본문 출력을 만든 버전 그대로 설치
```

NVIDIA GPU가 있는 리눅스·윈도우라면 부록 A.4절대로 `pyproject.toml`에 PyTorch 인덱스를 적어 주세요.

## 실행

장 폴더로 들어가서 `b`로 시작하는 파일을 **번호 순서대로** 실행합니다.
앞 블록이 저장한 모델이나 데이터를 뒤 블록이 쓰는 경우가 있거든요.

```bash
cd 09-cnn
uv run python b01_fc_params.py
```

- `b`로 시작하지 않는 파일(`학습도구.py`, `옷도구.py` 등)은 여러 블록이 함께 쓰는 모듈입니다. 직접 실행하지 않고 같은 폴더의 블록이 불러 씁니다. 다른 장에서 만든 모듈을 쓰는 장에는 그 모듈을 복사해 두었습니다.
- 데이터셋은 처음 실행할 때 `data/`에 내려받습니다. 여러 장이 같은 데이터를 쓰니 `BOOK_DATA_DIR` 환경 변수로 한 폴더를 가리키면 한 번만 받습니다(부록 A.9절).
- Hugging Face 모델(13·14·20장)은 처음 실행할 때 내려받습니다. 저장 위치는 부록 A.8절을 보세요.
- 20·21장의 `*_service` 폴더는 장 끝 실습 프로젝트로, 자기만의 `pyproject.toml`이 있습니다. 그 폴더에서 본문 순서대로 실행하세요.
  - 20장 `fashion_service`: 9장의 `fashion_cnn.pt`를 `models/`에 복사 → `uv run --extra torch python -m scripts.export_onnx` → `uv run --extra torch pytest -q`
  - 21장 `restaurant_service`: 21장 `b13_export.py`를 먼저 실행(추천 벡터를 `restaurant_service/artifacts/`에 저장) → 그 폴더에서 `uv run pytest -q`
  - Docker 빌드와 실행은 본문의 명령을 따르세요.

## 앞 장에서 만든 파일을 쓰는 장

책은 한 프로젝트 폴더에서 모든 장을 실행한다고 가정합니다. 이 예제는 장마다 폴더를 나눴으니,
아래 장은 앞 장을 먼저 실행한 뒤 그 장 폴더에서 파일을 복사해 오세요.

| 이 장을 실행하기 전에 | 복사할 파일 | 만드는 곳 |
|---|---|---|
| 9장 | `fashion_mlp.pt` | 6장 `06-nn-module` (6.11절) |
| 19장 | `fashion_cnn.pt`, `fashion_resnet.pt` | 9장 `09-cnn` (9.5절, 9.10절) |
| 20장 | `fashion_cnn.pt` | 9장 `09-cnn` (9.5절) |

19장 일부 예제는 FashionMNIST 원본 파일을 `data/FashionMNIST/raw/`에서 바로 읽습니다. `BOOK_DATA_DIR`로 다른 폴더를 쓴다면 그 폴더를 `data`라는 이름으로 이어 두세요(`ln -s "$BOOK_DATA_DIR" data`).

## 따라 하기 전에 알아 둘 것

- 시간을 재는 예제의 숫자는 컴퓨터마다 다릅니다. 학습 결과의 끝자리도 장치(CPU, MPS, CUDA)에 따라 조금씩 다를 수 있어요.
- 16·17장은 NVIDIA GPU가 있어야 하는 예제가 많습니다(17장의 여러 예제는 GPU 2장). `expected_errors.txt`에 GPU가 없으면 실패하는 파일과 이유를 적어 두었습니다. GPU가 없으면 부록 A.5절의 Colab을 쓰세요.

## 만든 방법

원고가 원본이고 이 폴더는 원고에서 자동으로 뽑았습니다(저장소의 `tools/extract_examples.py --vol 2`).
`tools/check_examples.py --vol 2`로 장마다 블록을 차례로 실행해 확인했습니다.
