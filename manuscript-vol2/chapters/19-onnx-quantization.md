# Chapter 19. 모델 내보내기와 경량화: ONNX와 양자화

> **학습 목표**  
> - 학습한 모델을 PyTorch 밖에서 돌려야 하는 이유와, ONNX 파일에 무엇이 담기는지 설명하기
> - `torch.onnx.export`로 모델을 내보내고, 묶음 크기 같은 차원을 자유롭게 열어 두기
> - ONNX Runtime으로 추론해 PyTorch 출력과 비교하고, torch 없이 모델 돌리기
> - 내보낼 수 없는 코드(데이터에 따라 갈리는 `if`, 파이썬 쪽 계산)를 알아보고 고치기
> - 그래프를 들여다보며 배치 정규화 접어 넣기와 연산 합치기 같은 최적화를 확인하기
> - 배율·영점·정수 행렬 곱·배율 단위로 양자화의 원리를 설명하기
> - torchao와 ONNX Runtime으로 양자화하고 크기·속도·정확도 표 만들기
> - 가지치기와 지식 증류의 아이디어를 작은 실험으로 확인하기

---

## 들어가며: 모델을 다 만들었는데, 어디서 돌리죠?

9장 9.10절에서 만든 작은 ResNet은 옷 사진을 93.04% 맞혔습니다. 이 모델을 친구가 만드는 쇼핑 앱에 넣고 싶다고 해 봅시다. 친구가 묻습니다. "그 모델 파일 주면 돼? 우리 앱은 파이썬이 아니라 다른 언어로 짰는데."

지금 가진 것은 `fashion_resnet.pt` 하나예요. 6장 6.10절에서 본 것처럼 이 파일에는 숫자(`state_dict`)만 있고, 그 숫자를 어떤 순서로 계산할지는 우리가 짠 파이썬 클래스 `작은_ResNet`에 들어 있습니다. 그러니 이 파일을 쓰려면 파이썬과 PyTorch, 그리고 우리 코드가 모두 필요해요. PyTorch가 얼마나 큰지부터 재 보겠습니다.

```python
from importlib import metadata

# 설치된 패키지 파일이 디스크에서 차지하는 크기 (이 책의 맥, 파이썬 3.12)
for 이름 in ["torch", "onnxruntime", "onnx", "numpy"]:
    배포판 = metadata.distribution(이름)
    크기 = sum(파일.size or 0 for 파일 in 배포판.files or [])
    print(f"{이름:12} {배포판.version:8} {크기 / 1024**2:6.1f} MB")
```

```text
torch        2.14.1    498.4 MB
onnxruntime  1.31.0     74.4 MB
onnx         1.23.2     25.0 MB
numpy        2.5.4      19.6 MB
```

이 맥에서 PyTorch는 약 500MB입니다. NVIDIA GPU용 리눅스 판은 CUDA 라이브러리가 따로 붙어서 몇 GB가 되기도 해요. 그런데 이 장에서 쓸 추론 엔진 **ONNX Runtime**은 74MB 남짓이고, 무엇보다 PyTorch 없이 돌아갑니다. 파이썬이 아닌 C++, C#, Java, JavaScript에서도 쓸 수 있어요.

음악에 비유해 보겠습니다. 작곡가가 피아노 앞에서 곡을 만들었다고 그 곡을 피아노로만 연주할 수 있는 건 아니죠. **악보**로 적어 두면 바이올린 연주자도, 오케스트라도 같은 곡을 연주합니다. PyTorch는 곡을 만드는(학습하는) 작업실이고, 이 장에서 만들 **ONNX 파일은 모델의 악보**예요. 악보를 받은 쪽은 작곡가의 작업실이 없어도 자기 악기(런타임)로 연주합니다.

이 장의 목표는 두 가지입니다.

- **밖으로**: 모델을 ONNX 파일로 내보내고, ONNX Runtime으로 PyTorch와 같은 답을 내는지 확인합니다.
- **작게**: 14장 14.6절에서 원리만 흉내 냈던 **양자화**를 진짜 도구로 해서, 모델을 4분의 1 크기로 줄이고 더 빠르게 돌립니다.

> **Q. 이 장에 필요한 패키지는 어떻게 설치하나요?**
> 프로젝트 폴더에서 `uv add onnx onnxscript onnxruntime torchao`를 실행하세요. `onnx`는 ONNX 파일을 읽고 쓰는 라이브러리, `onnxscript`는 PyTorch의 내보내기 기능이 안에서 쓰는 도구(없으면 내보내기가 오류를 냅니다), `onnxruntime`은 추론 엔진, `torchao`는 19.9절의 PyTorch 양자화 도구입니다. 이 장은 파이썬 3.12, PyTorch 2.14.1, onnx 1.23.2, onnxscript 0.7.2, onnxruntime 1.31.0, torchao 0.18.0에서 실행해 확인했어요. 라이선스는 onnx가 Apache-2.0, onnxscript와 onnxruntime이 MIT, torchao가 BSD-3-Clause입니다. 9장의 `옷도구.py`, `fashion_cnn.pt`(9.5절), `fashion_resnet.pt`(9.10절)를 이 장의 폴더에 함께 두세요.

## 19.1 ONNX: 모델의 악보

**ONNX(Open Neural Network Exchange)** 는 신경망을 담는 공개 파일 형식입니다. 여러 회사와 단체가 함께 만든 표준이라, 한 도구에서 만든 ONNX 파일을 다른 도구에서 읽을 수 있어요. ONNX 파일 하나에는 네 가지가 들어 있습니다.

- **계산 그래프**: `Conv` → `Relu` → `MaxPool` → … 처럼 어떤 연산을 어떤 순서로 이어서 하는지. 그래프의 마디 하나하나를 **노드(node)** 라고 부릅니다.
- **가중치**: 학습으로 정해진 숫자들. ONNX에서는 **이니셜라이저(initializer)** 라고 불러요.
- **입출력 정보**: 입력과 출력의 이름, 모양, 자료형.
- **연산자 판(opset) 번호**: `Conv`나 `Relu` 같은 연산의 정확한 뜻은 판마다 조금씩 다를 수 있어서, 이 파일이 몇 번째 판의 규칙으로 적혔는지 함께 적어 둡니다.

악보에 음표의 뜻이 정해져 있듯, ONNX는 `Conv`, `Gemm`(행렬 곱 + 덧셈) 같은 표준 연산자 수백 개의 뜻을 정해 두었습니다. 그래서 런타임은 파이썬 코드를 몰라도 그래프만 보고 계산할 수 있어요.

하나 더 중요한 점이 있습니다. 3장 3.11절과 6장 6.10절에서 "모르는 곳에서 받은 pickle 파일(`.pt`, joblib)은 여는 순간 그 안의 코드가 실행될 수 있다"고 했죠. ONNX 파일은 pickle이 아니라 **프로토콜 버퍼(protobuf)** 라는 데이터 형식이라, 파일을 읽는다고 그 안의 파이썬 코드가 실행되지는 않습니다. 담긴 것은 연산자 이름과 숫자뿐이에요. 다른 사람, 다른 언어와 모델을 주고받을 때 ONNX를 많이 쓰는 이유 중 하나입니다.

| 어디서 돌리나 | 무엇으로 돌리나 (예) |
|---|---|
| 파이썬 서버(PyTorch 없이) | ONNX Runtime (20장에서 FastAPI와 함께) |
| 다른 언어로 짠 프로그램 | ONNX Runtime의 C++, C#, Java, JavaScript API |
| 휴대폰, 작은 기기 | ONNX Runtime 모바일판, ExecuTorch, LiteRT, Core ML (19.12절) |
| 특정 회사의 가속기 | TensorRT(NVIDIA), OpenVINO(Intel) 같은 전용 도구 |

## 19.2 torch.onnx.export로 내보내기

### 첫 내보내기

9장 9.5절의 CNN(`fashion_cnn.pt`, 시험 정확도 91.01%)부터 내보내 보겠습니다. 필요한 것은 모델과, 모델에 넣을 **예시 입력** 하나예요.

```python
from pathlib import Path

import torch

from 옷도구 import 옷CNN

모델 = 옷CNN()
모델.load_state_dict(torch.load("fashion_cnn.pt", weights_only=True))   # 9장 9.5절의 CNN
모델.eval()                                       # 내보내기 전에 꼭 평가 모드로 (6장 6.8절)

예시_입력 = torch.zeros(1, 1, 28, 28)              # 사진 한 장 모양이면 값은 무엇이든 된다
결과 = torch.onnx.export(모델, (예시_입력,), "fashion_cnn_first.onnx", verbose=False)
print(type(결과).__name__)

for 파일 in ["fashion_cnn.pt", "fashion_cnn_first.onnx", "fashion_cnn_first.onnx.data"]:
    print(f"{파일:28} {Path(파일).stat().st_size / 1024:7.1f} KB")
```

```text
ONNXProgram
fashion_cnn.pt                1650.8 KB
fashion_cnn_first.onnx          16.1 KB
fashion_cnn_first.onnx.data   1646.6 KB
```

`torch.onnx.export`가 `ONNXProgram`이라는 객체를 돌려주고 파일 두 개를 만들었습니다. 무슨 일이 있었는지 순서대로 보면 이렇습니다.

1. **그래프 따기**: 예시 입력을 모델에 한 번 흘려보내면서, 어떤 텐서 연산이 어떤 순서로 일어나는지 기록합니다. PyTorch의 `torch.export`가 이 일을 해요. 예시 입력의 값은 상관없고 **모양과 자료형**만 중요하기 때문에 `torch.zeros`를 넣었습니다.
2. **분해**: 기록한 PyTorch 연산을 더 기본적인 연산으로 풀어 둡니다.
3. **번역**: 기본 연산을 ONNX 표준 연산자로 바꿉니다. 이때 `onnxscript`가 쓰여요.
4. **최적화**: 쓸데없는 노드를 지우고 합칠 수 있는 것을 합칩니다(19.6절에서 확인합니다).

이 방식은 PyTorch 2.9부터 기본값이 됐습니다. 그 전에는 TorchScript라는 다른 방식으로 그래프를 땄는데, 지금도 `dynamo=False`를 주면 쓸 수 있지만 "곧 없어질 기능"이라는 경고가 나와요. 인터넷의 옛 예제에서 이 옵션이나 `torch.jit`가 보이면 오래된 방식이라고 생각하면 됩니다.

> **Q. 내보내기 전에 왜 `model.eval()`을 하나요?**
> 6장 6.8절에서 본 것처럼 드롭아웃과 배치 정규화는 학습 모드와 평가 모드에서 다르게 동작합니다. 내보내기는 그 순간의 동작을 그래프로 굳히니, 학습 모드에서 내보내면 드롭아웃이 켜진 채로 굳어 버려요. 실제로 학습 모드인 모델을 내보내면 PyTorch가 "평가 모드로 바꾸는 것을 권한다"는 경고를 냅니다. 배포할 모델은 언제나 평가 모드로 내보내세요.

### 가중치는 어디에: .onnx와 .onnx.data

파일 크기를 보세요. `fashion_cnn_first.onnx`는 16KB밖에 안 되고, 1.6MB짜리 가중치는 옆의 `.onnx.data` 파일에 따로 들어갔습니다. `torch.onnx.export`의 `external_data` 옵션이 기본으로 켜져 있어서 그래요. ONNX가 쓰는 프로토콜 버퍼는 파일 하나가 2GB를 넘을 수 없어서, 큰 모델은 그래프와 가중치를 나눠 담아야 하거든요. 14장의 LLM 같은 모델이라면 꼭 필요한 기능입니다.

대신 두 파일은 **항상 함께 다녀야** 합니다. `.onnx`만 복사해 가면 가중치가 없어서 열리지 않아요. 우리 모델은 작으니 `external_data=False`로 한 파일에 담겠습니다. 담은 뒤에는 `onnx.checker`로 규격에 맞는지 검사하고, 파일에 적힌 정보를 읽어 볼게요.

```python
from pathlib import Path

import onnx
import torch

from 옷도구 import 옷CNN

모델 = 옷CNN()
모델.load_state_dict(torch.load("fashion_cnn.pt", weights_only=True))
모델.eval()
torch.onnx.export(모델, (torch.zeros(1, 1, 28, 28),), "fashion_cnn.onnx",
                  verbose=False, external_data=False)        # 가중치까지 한 파일에
print(f"fashion_cnn.onnx {Path('fashion_cnn.onnx').stat().st_size / 1024:.1f} KB")

모형 = onnx.load("fashion_cnn.onnx")
onnx.checker.check_model(모형)                    # ONNX 규격에 맞는지 검사 (틀리면 예외)
print("규격 검사 통과")
print("만든 도구:", 모형.producer_name, 모형.producer_version)
print("연산자 판(opset):", [(o.domain or "ai.onnx", o.version) for o in 모형.opset_import])


def 모양(값: onnx.ValueInfoProto) -> list[int | str]:
    """입출력 정보에서 차원 크기(또는 이름)를 꺼낸다."""
    return [d.dim_value or d.dim_param for d in 값.type.tensor_type.shape.dim]


print("입력:", [(i.name, 모양(i)) for i in 모형.graph.input])
print("출력:", [(o.name, 모양(o)) for o in 모형.graph.output])
```

```text
fashion_cnn.onnx 1662.3 KB
규격 검사 통과
만든 도구: pytorch 2.14.1
연산자 판(opset): [('ai.onnx', 20)]
입력: [('x', [1, 1, 28, 28])]
출력: [('linear_1', [1, 10])]
```

가중치까지 한 파일에 들어가니 1,662KB가 됐습니다. `.pt` 파일과 거의 같은 크기죠. 같은 숫자 42만 개를 float32로 담았으니 당연합니다. 파일에는 이 파일을 만든 도구(PyTorch 2.14.1)와 연산자 판 번호(20)가 적혀 있어요. 런타임은 이 번호를 보고 자기가 그 판을 지원하는지 판단합니다.

입출력 정보도 보세요. 입력 이름은 `forward(self, x)`의 인자 이름을 따서 `x`, 출력 이름은 마지막 층에서 따온 `linear_1`이 됐고, 모양은 예시 입력 그대로 `[1, 1, 28, 28]`로 **고정**되었습니다. 이름과 모양은 19.4절에서 손보겠습니다.

## 19.3 ONNX Runtime으로 추론하기

### 같은 답을 내는지 확인하기

악보가 제대로 적혔는지 확인하는 방법은 연주해 보는 것이죠. **ONNX Runtime**으로 파일을 열어 시험 사진 한 장을 넣고, PyTorch 모델의 답과 비교하겠습니다. ONNX Runtime에서 모델을 연 것을 **세션(session)** 이라고 불러요.

```python
import numpy as np
import onnxruntime as ort
import torch

from 옷도구 import 옷CNN, 시험_데이터

모델 = 옷CNN()
모델.load_state_dict(torch.load("fashion_cnn.pt", weights_only=True))
모델.eval()

세션 = ort.InferenceSession("fashion_cnn.onnx", providers=["CPUExecutionProvider"])
입력, 출력 = 세션.get_inputs()[0], 세션.get_outputs()[0]
print("입력:", 입력.name, 입력.shape, 입력.type)
print("출력:", 출력.name, 출력.shape, 출력.type)

X, y = 시험_데이터()
사진 = X[:1]                                      # 시험 사진 첫 장, (1, 1, 28, 28)
점수_onnx = 세션.run(None, {입력.name: 사진.numpy()})[0]    # 넘파이 배열로 넣고 넘파이로 받는다
with torch.no_grad():
    점수_torch = 모델(사진).numpy()

이름 = ["T셔츠", "바지", "풀오버", "드레스", "코트", "샌들", "셔츠", "운동화", "가방", "앵클부츠"]
np.set_printoptions(precision=3, suppress=True)
print("ONNX Runtime:", 점수_onnx[0])
print("PyTorch     :", 점수_torch[0])
print("가장 큰 차이:", np.abs(점수_onnx - 점수_torch).max())
print("예측:", 이름[점수_onnx.argmax()], "/ 정답:", 이름[y[0]])
```

```text
입력: x [1, 1, 28, 28] tensor(float)
출력: linear_1 [1, 10] tensor(float)
ONNX Runtime: [-3.732 -8.279 -7.15  -7.188 -8.329 -0.003 -5.677  2.529 -5.237  8.533]
PyTorch     : [-3.732 -8.279 -7.15  -7.188 -8.329 -0.003 -5.677  2.529 -5.237  8.533]
가장 큰 차이: 9.059906e-06
예측: 앵클부츠 / 정답: 앵클부츠
```

`InferenceSession`에 파일 경로와 **실행 장치(execution provider)** 목록을 주면 세션이 만들어집니다. 여기서는 CPU를 골랐어요. 세션은 입력과 출력의 이름·모양·자료형을 알려 주는데, `tensor(float)`가 PyTorch의 `float32`입니다.

`run`의 사용법이 PyTorch와 조금 다릅니다. 첫 인자는 받고 싶은 출력 이름 목록인데 `None`이면 전부 돌려주고, 둘째 인자는 `{입력 이름: 넘파이 배열}` 딕셔너리예요. 결과도 넘파이 배열의 **리스트**라서 `[0]`으로 첫 출력을 꺼냈습니다. ONNX Runtime은 텐서가 아니라 1권 20장의 넘파이 배열을 주고받아요.

두 점수는 소수 셋째 자리까지 똑같고, 가장 큰 차이는 백만분의 몇 수준입니다. 완전히 0이 아닌 이유는 4장 4.3절에서 본 float32의 끝자리 오차 때문이에요. 같은 곱셈과 덧셈이라도 **더하는 순서**가 다르면 끝자리가 조금 달라지는데, PyTorch와 ONNX Runtime은 계산을 나누고 모으는 방식이 서로 다릅니다. 이 정도 차이는 정상이고, 예측(앵클부츠)은 당연히 같아요.

### torch 없이 돌리기

이제 이 장의 핵심을 확인할 차례입니다. 정말 PyTorch 없이 돌아갈까요? 아래 코드는 `torch`도 `torchvision`도 불러오지 않습니다. FashionMNIST 시험 사진은 6장 6.11절에서 받아 둔 원본 파일을 넘파이로 직접 읽어요. 원본 파일은 앞부분에 개수와 크기를 적은 머리말(사진 파일 16바이트, 정답 파일 8바이트)이 있고, 그 뒤로 픽셀 값이 한 바이트씩 이어집니다.

```python
import sys

import numpy as np
import onnxruntime as ort

# torch 없이 FashionMNIST 원본 파일을 넘파이로 읽는다 (앞부분 16바이트, 8바이트는 머리말)
사진 = np.fromfile("data/FashionMNIST/raw/t10k-images-idx3-ubyte", dtype=np.uint8, offset=16)
정답 = np.fromfile("data/FashionMNIST/raw/t10k-labels-idx1-ubyte", dtype=np.uint8, offset=8)
사진 = 사진.reshape(-1, 1, 28, 28).astype(np.float32) / 255     # ToTensor()와 같은 0~1 실수

세션 = ort.InferenceSession("fashion_cnn.onnx", providers=["CPUExecutionProvider"])
입력이름 = 세션.get_inputs()[0].name
예측 = np.array([세션.run(None, {입력이름: 사진[i:i + 1]})[0].argmax()
                 for i in range(len(사진))])               # 한 장씩 1만 번
print(f"사진 {len(사진):,}장, 정확도 {(예측 == 정답).mean():.2%}")
print("torch를 불러왔나:", "torch" in sys.modules)
```

```text
사진 10,000장, 정확도 91.01%
torch를 불러왔나: False
```

정확도 91.01%. 9장에서 PyTorch로 잰 숫자와 똑같습니다. 마지막 줄의 `sys.modules`는 지금까지 불러온 모듈의 목록인데, 거기에 `torch`가 없어요. 이 프로그램이 돌아가는 데 필요한 것은 넘파이, ONNX Runtime, 그리고 `fashion_cnn.onnx` 파일 하나뿐입니다.

전처리를 눈여겨보세요. `/ 255`로 0~1 사이 실수로 바꾸는 일은 학습 때 `ToTensor()`가 해 주던 일입니다. 모델 바깥에서 하던 전처리는 ONNX 파일에 들어가지 않으니, **배포하는 쪽에서 똑같이 다시 짜야** 해요. 10장 10.2절에서 "모델이 배운 기준 그대로" 입력을 맞춰야 한다고 했던 것이 여기서도 그대로 적용됩니다. 전처리를 틀리면 어떻게 되는지는 19.10절에서 뜻밖의 모습으로 다시 보게 됩니다.

그런데 사진 1만 장을 한 장씩 1만 번 넣었습니다. 묶어서 한 번에 넣으면 안 될까요?

## 19.4 입력 모양 정하기

### 모양이 고정된 모델

앞에서 만든 `fashion_cnn.onnx`에 사진 64장 묶음을 넣어 보겠습니다. 실수로 float64 배열을 넣는 경우도 함께 보죠.

```python
import numpy as np
import onnxruntime as ort

세션 = ort.InferenceSession("fashion_cnn.onnx", providers=["CPUExecutionProvider"])
입력이름 = 세션.get_inputs()[0].name

for 설명, 입력 in [("64장 묶음", np.zeros((64, 1, 28, 28), dtype=np.float32)),
                   ("float64", np.zeros((1, 1, 28, 28), dtype=np.float64))]:
    try:
        세션.run(None, {입력이름: 입력})
    except Exception as e:
        print(f"[{설명}] {type(e).__name__}")
        print(" ", str(e).replace("\n", " ").split(" : ")[-1])
```

```text
[64장 묶음] InvalidArgument
  Got invalid dimensions for input: x for the following indices  index: 0 Got: 64 Expected: 1  Please fix either the inputs/outputs or the model.
[float64] InvalidArgument
  Unexpected input data type. Actual: (tensor(double)) , expected: (tensor(float))
```

두 번 다 `InvalidArgument` 오류입니다. 첫 번째는 "0번 차원에 64가 왔는데 1이어야 한다", 두 번째는 "double(float64)이 왔는데 float(float32)이어야 한다"는 뜻이에요. 4장 4.10절의 요령대로 숫자와 자료형 이름부터 읽으면 바로 보입니다. 넘파이의 기본 실수가 float64라서 두 번째 실수는 정말 자주 일어나요(4장 4.1절). 배포 코드에서는 `astype(np.float32)`를 습관처럼 붙이세요.

첫 번째 오류의 원인은 내보낼 때 넣은 예시 입력이 `(1, 1, 28, 28)`이었기 때문입니다. `torch.export`는 예시 입력의 모양을 보고 "이 모델은 언제나 사진 1장을 받는다"고 기록했어요.

### 자유로운 차원 열어 두기

묶음 크기는 실행할 때마다 달라질 수 있어야 합니다. 이렇게 크기를 미리 정하지 않는 차원을 **동적 차원(dynamic dimension)** 이라고 하고, `dynamic_shapes`로 알려 줘요. 입력과 출력의 이름도 알아보기 쉽게 바꾸겠습니다.

```python
import onnx
import onnxruntime as ort
import torch

from 옷도구 import 옷CNN, 시험_데이터

모델 = 옷CNN()
모델.load_state_dict(torch.load("fashion_cnn.pt", weights_only=True))
모델.eval()

묶음 = torch.export.Dim("batch")                  # 이름 붙인 "자유로운 차원"
torch.onnx.export(모델, (torch.zeros(1, 1, 28, 28),), "fashion_cnn_batch.onnx",
                  verbose=False, external_data=False,
                  input_names=["사진"], output_names=["점수"],
                  dynamic_shapes={"x": {0: 묶음}})       # forward(x)의 0번 차원은 자유

모형 = onnx.load("fashion_cnn_batch.onnx")
for 값 in [*모형.graph.input, *모형.graph.output]:
    print(값.name, [d.dim_value or d.dim_param for d in 값.type.tensor_type.shape.dim])

세션 = ort.InferenceSession("fashion_cnn_batch.onnx", providers=["CPUExecutionProvider"])
X, y = 시험_데이터()
for 장수 in [1, 7, 64]:
    print(f"{장수:>5}장 →", 세션.run(None, {"사진": X[:장수].numpy()})[0].shape)
점수 = 세션.run(["점수"], {"사진": X.numpy()})[0]           # 1만 장을 한 번에
print(f"1만 장 한 번에: {점수.shape}, 정확도 {(점수.argmax(axis=1) == y.numpy()).mean():.2%}")
```

```text
사진 ['batch', 1, 28, 28]
점수 ['batch', 10]
    1장 → (1, 10)
    7장 → (7, 10)
   64장 → (64, 10)
1만 장 한 번에: (10000, 10), 정확도 91.01%
```

입력 모양이 `['batch', 1, 28, 28]`, 출력이 `['batch', 10]`이 됐습니다. 0번 자리에 숫자 대신 이름이 적혀 있으면 "아무 크기나 된다"는 뜻이에요. 실제로 1장, 7장, 64장을 넣어도 모두 돌아가고, 1만 장을 한 번에 넣어 앞 절과 같은 91.01%를 얻었습니다. `run`의 첫 인자에 `["점수"]`처럼 출력 이름을 적으면 그 출력만 받아요.

`dynamic_shapes`는 "어느 입력의 몇 번 차원이 자유로운가"를 적는 딕셔너리입니다. 열쇠 `"x"`는 `forward(self, x)`의 **인자 이름**이고, 값 `{0: 묶음}`은 그 인자의 0번 차원이 `묶음`이라는 이름의 자유로운 차원이라는 뜻이에요. 입력이 여럿이면 열쇠도 여럿이 됩니다. 11~13장의 문장 모델이라면 `{0: 묶음, 1: 길이}`처럼 문장 길이 차원도 열어 두겠죠. `input_names`, `output_names`는 ONNX 파일 안에서 쓸 이름일 뿐이라 한글도 됩니다. 다만 다른 언어로 짠 프로그램이 이 파일을 읽을 때는 영어 이름이 다루기 편해서, 20장 서빙에서는 같은 방식으로 내보내되 입출력 이름만 영어(`image`, `logits`)로 바꿉니다.

> **Q. 다른 예제에서는 `dynamic_axes={"input": {0: "batch"}}`라고 쓰던데요?**
> 예전 TorchScript 방식에서 쓰던 옵션입니다. 지금 방식에서도 받아 주기는 하지만 안에서 `dynamic_shapes`로 바꿔 쓰면서 "권하지 않는다"는 경고를 내요. 새로 짜는 코드에서는 `dynamic_shapes`를 쓰세요. 인자 이름 대신 순서로 적고 싶으면 `dynamic_shapes=({0: 묶음},)`처럼 튜플로 써도 됩니다.

## 19.5 내보낼 수 있는 코드, 없는 코드

### 데이터에 따라 갈리는 if

19.2절에서 `torch.export`가 "예시 입력을 한 번 흘려보내면서 일어나는 텐서 연산을 기록한다"고 했습니다. 그렇다면 입력에 따라 다른 길로 가는 모델은 어떻게 될까요? 길이 하나만 기록될 텐데요. "입력의 합이 양수면 두 배, 아니면 1을 빼는" 작은 모델을 세 가지로 짜서 내보내 보겠습니다.

```python
import numpy as np
import onnx
import onnxruntime as ort
import torch
from torch import nn


class 파이썬_if(nn.Module):
    """합이 양수면 두 배, 아니면 1을 뺀다: 파이썬 if로."""

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.sum() > 0:
            return x * 2
        return x - 1


class 텐서_where(nn.Module):
    """같은 일을 torch.where로: 두 결과를 다 계산하고 칸마다 고른다 (4장 4.4절)."""

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return torch.where(x.sum() > 0, x * 2, x - 1)


class 텐서_cond(nn.Module):
    """같은 일을 torch.cond로: 조건에 따라 둘 중 한 갈래만 계산한다."""

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return torch.cond(x.sum() > 0, lambda x: x * 2, lambda x: x - 1, (x,))


for 모델 in [파이썬_if(), 텐서_where(), 텐서_cond()]:
    이름 = type(모델).__name__
    try:
        torch.onnx.export(모델.eval(), (torch.ones(3),), "branch.onnx",
                          verbose=False, external_data=False)
    except Exception as e:
        print(f"{이름}: 내보내기 실패 ({type(e).__name__} ← {type(e.__cause__).__name__})")
        continue
    연산 = [노드.op_type for 노드 in onnx.load("branch.onnx").graph.node]
    세션 = ort.InferenceSession("branch.onnx", providers=["CPUExecutionProvider"])
    입력이름 = 세션.get_inputs()[0].name
    결과 = [세션.run(None, {입력이름: np.array(v, dtype=np.float32)})[0].tolist()
            for v in ([1, 2, 3], [-1, -2, -3])]
    print(f"{이름}: {연산} → {결과}")
```

```text
파이썬_if: 내보내기 실패 (TorchExportError ← GuardOnDataDependentSymNode)
텐서_where: ['ReduceSum', 'Greater', 'Mul', 'Sub', 'Where'] → [[2.0, 4.0, 6.0], [-2.0, -3.0, -4.0]]
텐서_cond: ['ReduceSum', 'Greater', 'If'] → [[2.0, 4.0, 6.0], [-2.0, -3.0, -4.0]]
```

파이썬 `if`로 짠 모델은 내보내기에 실패했습니다. 오류의 속 원인 `GuardOnDataDependentSymNode`는 "데이터 값에 따라 정해지는 것에 기대고 있다"는 뜻이에요. `x.sum() > 0`이 참인지 거짓인지는 실제 숫자를 넣어 봐야 알 수 있는데, 그래프에는 두 갈래 중 하나만 적을 수 있으니 내보내기가 거절한 겁니다. 조용히 한쪽 길만 굳혀 버리는 것보다 이렇게 실패하는 편이 훨씬 안전해요.

나머지 둘은 성공했고, 양수·음수 입력 모두에서 올바른 답을 냈습니다.

- **`torch.where`** 는 4장 4.4절에서 본 그 함수예요. 두 갈래(`x * 2`와 `x - 1`)를 **모두 계산한 뒤** 조건에 따라 고릅니다. 그래프에 `Mul`, `Sub`, `Where`가 다 들어 있죠. 갈래가 가벼울 때 가장 간단한 해결책입니다.
- **`torch.cond`** 는 조건에 따라 **한 갈래만 계산하는** 연산이에요. ONNX 그래프에 `If` 노드 하나가 생기고, 그 안에 두 갈래가 작은 그래프로 들어갑니다. 갈래가 무거워서 둘 다 계산하기 아까울 때 씁니다.

### 파이썬 코드는 내보낼 때 한 번만 돈다

반대로 실패하지 않아서 더 조심해야 하는 경우도 있습니다. `forward` 안에 텐서 연산이 아닌 **파이썬 코드**가 섞여 있을 때예요.

```python
import numpy as np
import onnx
import onnxruntime as ort
import torch
from torch import nn


class 굳는_모델(nn.Module):
    """forward 안에 파이썬 코드가 섞인 모델."""

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        print("  (forward 실행됨)")
        잡음 = torch.from_numpy(np.random.rand(3).astype(np.float32))   # 넘파이 난수
        for _ in range(3):                                            # 파이썬 반복문
            x = x + 1
        return x + 잡음


print("내보내는 중:")
torch.onnx.export(굳는_모델().eval(), (torch.zeros(3),), "frozen.onnx",
                  verbose=False, external_data=False)
그래프 = onnx.load("frozen.onnx").graph
print("연산:", [노드.op_type for 노드 in 그래프.node])
print("저장된 상수:", [(값.name, list(값.dims)) for 값 in 그래프.initializer])

세션 = ort.InferenceSession("frozen.onnx", providers=["CPUExecutionProvider"])
입력이름 = 세션.get_inputs()[0].name
for 회 in range(1, 3):
    print(f"{회}번째 실행:", 세션.run(None, {입력이름: np.zeros(3, dtype=np.float32)})[0])
```

```text
내보내는 중:
  (forward 실행됨)
연산: ['Add', 'Add', 'Add', 'Add']
저장된 상수: [('clone', [3]), ('scalar_tensor_default', [])]
1번째 실행: [3.3831162 3.3439608 3.2308836]
2번째 실행: [3.3831162 3.3439608 3.2308836]
```

세 가지를 보세요.

- `print`는 내보낼 때 **한 번** 실행됐고, ONNX 그래프에는 남지 않았습니다. 세션을 두 번 실행할 때는 아무것도 찍히지 않았죠.
- 파이썬 `for` 반복문은 세 번 돌면서 `Add`를 세 개 기록했습니다. 반복문 자체가 아니라 **펼쳐진 결과**가 그래프에 남은 거예요. 반복 횟수가 입력과 상관없이 정해져 있다면 문제없습니다.
- 가장 위험한 것은 넘파이 난수입니다. `np.random.rand(3)`은 텐서 연산이 아니라서, 내보낼 때 한 번 뽑힌 숫자가 `clone`이라는 **상수**로 굳어 버렸어요. 1번째와 2번째 실행의 결과가 똑같죠. 매번 다른 잡음을 더하려던 의도가 조용히 사라졌는데 오류는 하나도 없습니다.

정리하면, `forward` 안에서는 **텐서 연산만으로** 계산하는 것이 내보내기의 기본 규칙입니다. 넘파이, `math`, `random` 같은 파이썬 쪽 계산은 상수로 굳고, 텐서 값에 따라 갈리는 `if`는 실패해요. 모양에 따라 갈리는 `if`(예: `if x.shape[1] > 100`)는 예시 입력의 모양 기준으로 한쪽이 굳으니, 동적 차원을 열어 둔 모델에서는 특히 조심해야 합니다. 내보낸 뒤에는 항상 **여러 입력으로 PyTorch와 결과를 비교**하는 습관을 들이세요. 19.3절에서 한 비교가 바로 그 검사입니다.

## 19.6 그래프 들여다보기

### 이 장의 도구 모음

지금까지 내보내기 코드를 매번 길게 썼습니다. 19.2~19.4절에서 정한 것(한 파일, 평가 모드, 묶음 차원 열기, 입출력 이름)을 함수 하나로 묶고, 9장의 작은 ResNet 설계도와 시간 재는 함수도 함께 `배포도구.py`에 모아 두겠습니다. 9장의 `옷도구.py`처럼 이 장의 나머지 예제가 이 파일을 `import`해요.

```python
"""19장 예제에서 함께 쓰는 모델 설계도·내보내기·시간 재기 도구."""
import statistics
import time
from collections.abc import Callable
from pathlib import Path

import numpy as np
import onnxruntime as ort
import torch
import torch.nn.functional as F
from torch import nn

from 옷도구 import 옷CNN, 시험_데이터  # noqa: F401  (9장 9.5절의 CNN과 시험 데이터)


class 잔차블록(nn.Module):
    """9장 9.8절의 잔차 블록."""

    def __init__(self, 입력: int, 출력: int, 보폭: int = 1) -> None:
        super().__init__()
        self.합성곱1 = nn.Conv2d(입력, 출력, 3, stride=보폭, padding=1, bias=False)
        self.정규화1 = nn.BatchNorm2d(출력)
        self.합성곱2 = nn.Conv2d(출력, 출력, 3, padding=1, bias=False)
        self.정규화2 = nn.BatchNorm2d(출력)
        if 보폭 != 1 or 입력 != 출력:
            self.지름길 = nn.Sequential(nn.Conv2d(입력, 출력, 1, stride=보폭, bias=False),
                                        nn.BatchNorm2d(출력))
        else:
            self.지름길 = nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        고칠양 = self.정규화2(self.합성곱2(F.relu(self.정규화1(self.합성곱1(x)))))
        return F.relu(고칠양 + self.지름길(x))


def 작은_ResNet() -> nn.Sequential:
    """9장 9.10절의 작은 ResNet 설계도."""
    return nn.Sequential(
        nn.Conv2d(1, 32, 3, padding=1, bias=False), nn.BatchNorm2d(32), nn.ReLU(),
        잔차블록(32, 32), 잔차블록(32, 64, 보폭=2), 잔차블록(64, 128, 보폭=2),
        nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Dropout(0.3), nn.Linear(128, 10),
    )


def 불러오기(설계도: Callable[[], nn.Module], 파일: str) -> nn.Module:
    """저장한 가중치를 설계도에 채우고 평가 모드로 돌려준다."""
    모델 = 설계도()
    모델.load_state_dict(torch.load(파일, weights_only=True))
    return 모델.eval()


def ONNX로_내보내기(모델: nn.Module, 경로: str, 최적화: bool = True) -> None:
    """19.2~19.4절의 정리: 묶음 크기가 자유로운 한 파일짜리 ONNX로 내보낸다."""
    torch.onnx.export(모델, (torch.zeros(1, 1, 28, 28),), 경로, verbose=False,
                      external_data=False, optimize=최적화,
                      input_names=["사진"], output_names=["점수"],
                      dynamic_shapes=({0: torch.export.Dim("batch")},))


def 세션_만들기(경로: str, 스레드: int = 4) -> ort.InferenceSession:
    """스레드 수를 정해 CPU에서 돌리는 ONNX Runtime 세션."""
    설정 = ort.SessionOptions()
    설정.intra_op_num_threads = 스레드
    return ort.InferenceSession(경로, 설정, providers=["CPUExecutionProvider"])


def 세션_정확도(세션: ort.InferenceSession, X: np.ndarray, y: np.ndarray) -> float:
    """사진 묶음 전체를 한 번에 넣어 정확도를 잰다."""
    점수 = 세션.run(None, {"사진": X})[0]
    return float((점수.argmax(axis=1) == y).mean())


def 시간_재기(함수: Callable[[], object], 반복: int = 50, 준비: int = 5) -> float:
    """준비 운동 뒤 여러 번 재서 한 번 실행 시간의 중앙값(밀리초)을 돌려준다."""
    for _ in range(준비):
        함수()
    기록 = []
    for _ in range(반복):
        시작 = time.perf_counter()
        함수()
        기록.append((time.perf_counter() - 시작) * 1000)
    return statistics.median(기록)


def 파일_크기(*경로: str) -> float:
    """파일 크기의 합(KB). .onnx와 옆의 .onnx.data를 함께 셀 때 쓴다."""
    return sum(Path(p).stat().st_size for p in 경로 if Path(p).exists()) / 1024
```

`작은_ResNet`과 `잔차블록`은 9장 9.10절의 코드 그대로입니다. 9장에서는 실습 코드 안에 있었는데, 저장한 `fashion_resnet.pt`를 불러오려면 같은 설계도가 필요해서 옮겨 왔어요. 이것이 6장 6.10절에서 말한 `state_dict` 방식의 약속입니다. 숫자만 저장했으니 설계도는 코드로 갖고 있어야 하죠. 반대로 ONNX 파일은 설계도(그래프)와 숫자를 함께 담으니, ONNX로 내보낸 다음부터는 이 클래스가 필요 없습니다.

`세션_만들기`는 ONNX Runtime이 쓸 스레드 수를 정하는 함수이고, `시간_재기`는 19.7절에서 설명합니다.

### 노드와 이니셜라이저

`onnx.load`로 연 파일은 파이썬 객체라서 안을 직접 들여다볼 수 있습니다. 9.5절 CNN의 그래프를 노드 순서대로 찍어 보겠습니다.

```python
import onnx

from 배포도구 import ONNX로_내보내기, 불러오기, 옷CNN

모델 = 불러오기(옷CNN, "fashion_cnn.pt")
ONNX로_내보내기(모델, "fashion_cnn.onnx")
그래프 = onnx.load("fashion_cnn.onnx").graph

print("[계산 순서]")
for 노드 in 그래프.node:
    print(f"  {노드.op_type:8} {', '.join(노드.input)} → {', '.join(노드.output)}")

print("[저장된 숫자]")
개수 = 0
for 값 in 그래프.initializer:
    배열 = onnx.numpy_helper.to_array(값)
    개수 += 배열.size
    print(f"  {값.name:22} {str(배열.shape):16} {배열.dtype}")
print(f"합계 {개수:,}개 / PyTorch 파라미터 {sum(p.numel() for p in 모델.parameters()):,}개")
```

```text
[계산 순서]
  Conv     사진, 특징.0.weight, 특징.0.bias → conv2d
  Relu     conv2d → relu
  MaxPool  relu → max_pool2d
  Conv     max_pool2d, 특징.3.weight, 특징.3.bias → conv2d_1
  Relu     conv2d_1 → relu_1
  MaxPool  relu_1 → max_pool2d_1
  Reshape  max_pool2d_1, val_7 → view
  Gemm     view, 분류.1.weight, 분류.1.bias → linear
  Relu     linear → relu_2
  Gemm     relu_2, 분류.3.weight, 분류.3.bias → 점수
[저장된 숫자]
  특징.0.weight            (32, 1, 3, 3)    float32
  특징.0.bias              (32,)            float32
  특징.3.weight            (64, 32, 3, 3)   float32
  특징.3.bias              (64,)            float32
  분류.1.weight            (128, 3136)      float32
  분류.1.bias              (128,)           float32
  분류.3.weight            (10, 128)        float32
  분류.3.bias              (10,)            float32
  val_7                  (2,)             int64
합계 421,644개 / PyTorch 파라미터 421,642개
```

"계산 순서"가 바로 악보입니다. 노드마다 연산자 이름과, 어떤 값을 받아(왼쪽) 어떤 값을 만드는지(오른쪽)가 적혀 있어요. 사진이 `Conv` → `Relu` → `MaxPool`을 두 번 지나고, `Reshape`로 한 줄로 펴진 뒤(`nn.Flatten`), `Gemm`(행렬 곱 + 편향) 두 번을 거쳐 `점수`가 됩니다. 9장 9.5절에서 따라가 본 모양 그대로죠. `Conv`의 입력에 `특징.0.weight` 같은 이름이 보이는데, PyTorch `state_dict`의 열쇠 이름이 그대로 이니셜라이저의 이름이 된 거예요.

이니셜라이저 숫자를 모두 세면 421,644개로, PyTorch 파라미터 421,642개보다 두 개 많습니다. 범인은 `val_7`이에요. `Reshape`에 "몇 행 몇 열로 펼지"를 알려 주는 정수 두 개(int64)가 상수로 들어간 겁니다. 학습할 숫자는 정확히 같아요.

이렇게 글자로 보는 것 말고 그림으로 보고 싶다면 **Netron**이라는 오픈소스 뷰어가 많이 쓰입니다. ONNX 파일을 열면 노드를 상자로, 값의 흐름을 화살표로 그려 줘요.

### 배치 정규화는 어디로 갔을까

이번에는 작은 ResNet을 내보내 보겠습니다. 이 모델에는 배치 정규화가 9개 있어요. `optimize` 옵션을 끈 것과 켠 것(기본값)을 비교합니다.

```python
from collections import Counter

import numpy as np
import onnx
import torch

from 배포도구 import ONNX로_내보내기, 불러오기, 세션_만들기, 작은_ResNet

모델 = 불러오기(작은_ResNet, "fashion_resnet.pt")        # 9장 9.10절의 작은 ResNet (93.04%)
x = torch.randn(8, 1, 28, 28)
with torch.no_grad():
    기준 = 모델(x).numpy()

for 최적화 in [False, True]:
    경로 = f"fashion_resnet_opt{int(최적화)}.onnx"
    ONNX로_내보내기(모델, 경로, 최적화=최적화)
    연산 = Counter(노드.op_type for 노드 in onnx.load(경로).graph.node)
    차이 = np.abs(세션_만들기(경로).run(None, {"사진": x.numpy()})[0] - 기준).max()
    print(f"optimize={최적화}: 노드 {sum(연산.values())}개, 최대 차이 {차이:.1e}")
    print("  ", dict(연산.most_common(6)))
```

```text
optimize=False: 노드 86개, 최대 차이 1.5e-05
   {'Expand': 18, 'Constant': 14, 'Shape': 10, 'CastLike': 9, 'Conv': 9, 'BatchNormalization': 9}
optimize=True: 노드 22개, 최대 차이 1.5e-05
   {'Conv': 9, 'Relu': 7, 'Add': 3, 'ReduceMean': 1, 'Reshape': 1, 'Gemm': 1}
```

최적화를 끄면 노드가 86개이고, `BatchNormalization`이 9개 보입니다. `Expand`, `Constant`, `Shape` 같은 것은 번역하면서 생긴 자질구레한 보조 노드예요. 최적화를 켜면 노드가 22개로 줄고, **`BatchNormalization`이 모두 사라졌습니다.** 그런데 결과는 둘 다 PyTorch와 최대 차이가 십만분의 1~2 수준으로 같아요. 배치 정규화 계산이 어디로 갔을까요?

8장 8.4절에서 배치 정규화는 "평균을 빼고 표준편차로 나눈 뒤 감마를 곱하고 베타를 더한다"고 했습니다. 평가 모드에서는 평균과 분산이 학습 중에 모아 둔 **고정된 숫자**(`running_mean`, `running_var`)라서, 결국 채널마다 "어떤 수를 곱하고 어떤 수를 더하는" 계산이 돼요. 그런데 합성곱도 채널마다 곱하고 더하는 계산이니, 둘을 하나로 합칠 수 있습니다. 손으로 해 보겠습니다.

```python
import torch
import torch.nn.functional as F

from 배포도구 import 불러오기, 작은_ResNet

모델 = 불러오기(작은_ResNet, "fashion_resnet.pt")
합성곱, 정규화 = 모델[0], 모델[1]                    # 첫 Conv2d(1→32)와 BatchNorm2d(32)

# 평가 모드의 배치 정규화: (x - 평균) / sqrt(분산 + eps) * 감마 + 베타 → 채널마다 곱하고 더하기
배율 = 정규화.weight / torch.sqrt(정규화.running_var + 정규화.eps)       # (32,)
새_가중치 = 합성곱.weight * 배율.view(-1, 1, 1, 1)                       # 출력 채널마다 곱하기
새_편향 = 정규화.bias - 정규화.running_mean * 배율                      # 원래 Conv는 bias=False

x = torch.randn(4, 1, 28, 28)
with torch.no_grad():
    두_단계 = 정규화(합성곱(x))
    한_단계 = F.conv2d(x, 새_가중치, 새_편향, padding=1)
print("합성곱 가중치:", tuple(새_가중치.shape), "편향:", tuple(새_편향.shape))
print("두 결과의 최대 차이:", (두_단계 - 한_단계).abs().max().item())
```

```text
합성곱 가중치: (32, 1, 3, 3) 편향: (32,)
두 결과의 최대 차이: 5.7220458984375e-06
```

배치 정규화의 "곱할 수"(`배율`)를 합성곱 가중치에 미리 곱해 두고, "더할 수"를 편향으로 만들었습니다. 이렇게 만든 합성곱 한 번이 원래의 합성곱 + 배치 정규화 두 단계와 백만분의 몇 차이로 같은 답을 냅니다. 이것을 **배치 정규화 접어 넣기(folding)** 라고 해요. 9장 9.7절에서 "배치 정규화 앞의 합성곱은 `bias=False`로 둔다"고 했는데, 접어 넣고 나면 배치 정규화의 베타가 그 합성곱의 편향 자리로 들어가는 셈입니다. 추론할 때는 층 하나가 통째로 사라지니 그만큼 빨라져요. 학습 중에는 평균과 분산이 배치마다 바뀌니 이 계산을 할 수 없고, 평가 모드로 굳힌 뒤에만 가능하다는 점도 기억해 두세요.

### ONNX Runtime이 한 번 더 다듬는다

내보낸 그래프는 ONNX Runtime이 세션을 만들 때 한 번 더 다듬습니다. 단계별로 실제로 돌릴 그래프를 파일로 저장하게 해서 비교해 보겠습니다.

```python
from collections import Counter

import onnx
import onnxruntime as ort

from 배포도구 import ONNX로_내보내기, 불러오기, 작은_ResNet

ONNX로_내보내기(불러오기(작은_ResNet, "fashion_resnet.pt"), "fashion_resnet.onnx")
단계들 = {"끄기": ort.GraphOptimizationLevel.ORT_DISABLE_ALL,
          "기본": ort.GraphOptimizationLevel.ORT_ENABLE_BASIC,
          "확장": ort.GraphOptimizationLevel.ORT_ENABLE_EXTENDED,
          "전부": ort.GraphOptimizationLevel.ORT_ENABLE_ALL}            # 세션의 기본값
for 이름, 단계 in 단계들.items():
    설정 = ort.SessionOptions()
    설정.graph_optimization_level = 단계
    설정.optimized_model_filepath = "fashion_resnet_ort.onnx"    # 실제로 돌릴 그래프를 저장
    ort.InferenceSession("fashion_resnet.onnx", 설정, providers=["CPUExecutionProvider"])
    연산 = Counter(노드.op_type for 노드 in onnx.load("fashion_resnet_ort.onnx").graph.node)
    print(f"{이름}: 노드 {sum(연산.values()):2}개 {dict(연산.most_common(4))}")
```

```text
끄기: 노드 22개 {'Conv': 9, 'Relu': 7, 'Add': 3, 'ReduceMean': 1}
기본: 노드 22개 {'Conv': 9, 'Relu': 7, 'Add': 3, 'ReduceMean': 1}
확장: 노드 18개 {'Conv': 5, 'FusedConv': 4, 'Add': 3, 'Relu': 3}
전부: 노드 12개 {'FusedConv': 7, 'Conv': 2, 'ReduceMean': 1, 'Reshape': 1}
```

"끄기"와 "기본"은 22개 그대로입니다. 기본 단계가 하는 정리(상수 계산 미리 하기, 쓸모없는 노드 지우기)는 PyTorch가 내보내면서 이미 해 두었기 때문이에요. "확장" 단계부터 `FusedConv`가 나타납니다. `Conv` 바로 뒤의 `Relu`를 합성곱 안으로 합친 노드예요. 합성곱 결과를 메모리에 썼다가 다시 읽어서 ReLU를 하는 대신, 쓰기 전에 바로 ReLU를 해 버리니 메모리를 오가는 횟수가 줄어듭니다. "전부" 단계에서는 잔차 연결의 `Add`까지 합성곱에 합쳐져 노드가 12개가 됐어요.

세션의 기본값이 이 "전부" 단계라서, 우리가 따로 설정하지 않아도 ONNX Runtime은 이렇게 다듬은 그래프로 계산합니다. 다만 "전부" 단계는 그 컴퓨터의 CPU에 맞춘 메모리 배치(레이아웃)까지 정하기 때문에, 이 단계의 그래프를 저장하면 "같은 환경에서만 쓰라"는 경고가 나와요. 그래서 배포할 때는 다듬기 전의 `.onnx` 파일을 나눠 주고, 다듬기는 각 컴퓨터의 런타임에 맡기는 것이 보통입니다.

## 19.7 얼마나 빨라졌나: 속도 재기

### 재는 방법부터

이제 PyTorch와 ONNX Runtime의 속도를 비교할 차례입니다. 4장 4.8절에서 GPU 시간을 잴 때 "준비 운동을 하고 재라"고 했죠. CPU에서도 첫 몇 번은 메모리를 잡고 캐시를 채우느라 느리기 때문에, `배포도구.py`의 `시간_재기`는 준비 운동 5번 뒤에 50번을 재서 **중앙값**을 돌려줍니다. 평균 대신 중앙값을 쓰는 건, 다른 프로그램이 잠깐 끼어들어 한두 번 크게 느려진 기록에 흔들리지 않게 하려는 거예요. 두 엔진의 스레드 수도 4개로 똑같이 맞췄습니다. 스레드 수가 다르면 공정한 비교가 아니니까요.

```python
import platform

import torch

from 배포도구 import (ONNX로_내보내기, 불러오기, 세션_만들기, 시간_재기, 시험_데이터,
                     옷CNN, 작은_ResNet)

torch.set_num_threads(4)                          # PyTorch와 ONNX Runtime 모두 스레드 4개
print("환경:", platform.machine(), platform.python_version(), "torch", torch.__version__)
X, _ = 시험_데이터()

print(f"{'모델':6} {'묶음':>4} {'PyTorch':>10} {'ORT':>10} {'배':>5}")
for 이름, 설계도, 파일 in [("CNN", 옷CNN, "fashion_cnn.pt"),
                          ("ResNet", 작은_ResNet, "fashion_resnet.pt")]:
    모델 = 불러오기(설계도, 파일)
    ONNX로_내보내기(모델, "speed.onnx")
    세션 = 세션_만들기("speed.onnx", 스레드=4)
    for 장수 in [1, 64]:
        x = X[:장수]
        x_np = x.numpy()
        with torch.inference_mode():
            파이토치 = 시간_재기(lambda: 모델(x))
        런타임 = 시간_재기(lambda: 세션.run(None, {"사진": x_np}))
        print(f"{이름:6} {장수:>4} {파이토치:8.3f}ms {런타임:8.3f}ms {파이토치 / 런타임:5.1f}")
```

```text
환경: arm64 3.12.10 torch 2.14.1
모델       묶음    PyTorch        ORT     배
CNN       1    0.111ms    0.060ms   1.8
CNN      64    3.683ms    1.650ms   2.2
ResNet    1    0.663ms    0.286ms   2.3
ResNet   64   36.491ms   15.151ms   2.4
```

이 숫자는 이 책의 실행 환경(Apple M4 Max, CPU, 스레드 4개)에서 잰 중앙값입니다. 같은 컴퓨터에서도 다른 프로그램이 함께 돌고 있으면 실행마다 꽤 흔들리고(특히 PyTorch 쪽이 그랬습니다), 다른 컴퓨터에서는 크게 달라질 수 있어요. 그래도 흐름은 분명합니다. **같은 모델, 같은 숫자인데 ONNX Runtime이 두 배쯤 빠릅니다.** 사진 1장을 넣을 때도, 64장을 넣을 때도 그래요.

어디서 이런 차이가 날까요? 앞 절에서 본 대로 ONNX Runtime은 그래프 전체를 미리 보고 배치 정규화를 접고, 합성곱과 ReLU와 덧셈을 합치고, 그 CPU에 맞는 계산 방식을 골라 둡니다. 반면 PyTorch의 기본 실행 방식은 파이썬이 `forward`를 한 줄씩 따라가며 연산을 하나씩 부르는 방식이라, 연산과 연산 사이에 매번 파이썬을 거치고 중간 결과를 메모리에 씁니다. 사진 1장처럼 계산이 작을수록 이 "사이 시간"의 비중이 커져요.

또 하나 보이는 것은 묶음의 힘입니다. ResNet에서 1장은 약 0.3ms, 64장은 약 15ms이니 한 장당 0.23ms쯤이에요. 묶어서 넣으면 한 장씩 넣을 때보다 장당 시간이 줄어듭니다. 19.3절처럼 1만 장을 한 장씩 넣는 대신 19.4절에서 묶음 차원을 열어 둔 이유죠. 20장에서 서버를 만들 때 여러 요청을 묶어 처리하는 **배치 추론**이 이 원리를 씁니다.

> **Q. PyTorch도 그래프를 미리 보고 합치면 되지 않나요?**
> 그런 기능이 있습니다. `torch.compile`이 바로 "PyTorch 모델을 그래프로 따서 합치고 다듬는" 도구예요. 학습과 GPU에서 특히 힘을 발휘하는데, 16장 GPU와 성능에서 다룹니다. 이 장에서는 "PyTorch가 없는 곳에서 돌린다"는 목표가 먼저라 ONNX Runtime을 썼습니다.

## 19.8 양자화 다시 보기: 눈금, 영점, 정수 계산

### 14장의 흉내에서 진짜 양자화로

14장 14.6절에서 양자화를 "자에 눈금을 새기는 것"에 비유하고, 가중치를 행마다 -127~127 눈금에 맞췄다가 다시 실수로 되돌려 봤습니다. 그때 두 가지 숙제를 남겼어요. 실수로 되돌려 넣었으니 **메모리가 줄지 않았고**, 행마다 배율을 하나만 써서 **int4가 망가졌다**는 것이었죠. 진짜 양자화 도구는 정수와 배율만 저장하고, 계산도 가능한 한 정수로 합니다. 그러려면 개념 세 가지가 더 필요해요.

### 영점: 0 이상인 값을 위한 눈금

가중치는 0을 가운데 두고 양수와 음수가 섞여 있어서 -127~127 눈금이 잘 맞았습니다. 그런데 층과 층 사이를 흐르는 값(**활성값**)은 사정이 달라요. ReLU를 지난 값은 모두 0 이상이거든요. 0 이상인 값에 -127~127 눈금을 쓰면 음수 쪽 눈금 절반을 버리게 됩니다. 이럴 때는 0~255 눈금(uint8)을 쓰고, "실수 0이 몇 번 눈금에 놓이는지"를 따로 기억합니다. 이 번호를 **영점(zero point)** 이라고 해요.

```python
import torch

torch.manual_seed(0)
# ReLU를 지난 값: 0 이상만 있다 (예제용으로 만든 0~6 사이 값)
활성값 = torch.rand(10_000) ** 2 * 6


def 대칭_int8(x: torch.Tensor) -> tuple[torch.Tensor, float]:
    """14장 14.6절 방식: 0을 가운데 두고 -127~127 눈금."""
    배율 = x.abs().max().item() / 127
    return (x / 배율).round().clamp(-127, 127), 배율


def 비대칭_uint8(x: torch.Tensor) -> tuple[torch.Tensor, float, int]:
    """최솟값~최댓값을 0~255 눈금에 맞추고, 실수 0이 놓일 눈금(영점)을 기억한다."""
    작은, 큰 = min(x.min().item(), 0.0), max(x.max().item(), 0.0)   # 실수 0은 꼭 범위 안에
    배율 = (큰 - 작은) / 255
    영점 = round(-작은 / 배율)
    return (x / 배율 + 영점).round().clamp(0, 255), 배율, 영점


정수, 배율 = 대칭_int8(활성값)
print(f"대칭 int8   : 배율 {배율:.5f}, 쓰인 눈금 {정수.unique().numel():3}개, "
      f"평균 오차 {(정수 * 배율 - 활성값).abs().mean():.5f}")
정수, 배율, 영점 = 비대칭_uint8(활성값)
print(f"비대칭 uint8: 배율 {배율:.5f}, 쓰인 눈금 {정수.unique().numel():3}개, "
      f"평균 오차 {((정수 - 영점) * 배율 - 활성값).abs().mean():.5f}, 영점 {영점}")

# 음수도 있는 값이라면 영점이 가운데쯤으로 온다
_, 배율, 영점 = 비대칭_uint8(torch.tensor([-1.0, 0.0, 3.0]))
print(f"-1~3 범위: 배율 {배율:.5f}, 영점 {영점} (실수 0 → 정수 {영점})")
```

```text
대칭 int8   : 배율 0.04724, 쓰인 눈금 128개, 평균 오차 0.01163
비대칭 uint8: 배율 0.02353, 쓰인 눈금 256개, 평균 오차 0.00576, 영점 0
-1~3 범위: 배율 0.01569, 영점 64 (실수 0 → 정수 64)
```

예제용으로 0~6 사이의 값 1만 개를 만들었습니다. 대칭 int8 방식은 256개 눈금 중 0~127, 128개만 썼어요. 비대칭 uint8 방식은 256개를 다 쓰니 눈금 간격(배율)이 절반이 되고, 평균 오차도 0.01163에서 0.00576으로 절반이 됐습니다. 같은 1바이트로 두 배 정밀하게 담은 거예요.

이 값들은 0에서 시작하니 영점은 0입니다. 마지막 줄처럼 -1~3 범위라면 영점이 64가 돼요. 정수 64가 실수 0을 뜻하고, 정수 0은 실수 -1 근처, 정수 255는 3 근처를 뜻합니다. 실수 = (정수 - 영점) × 배율, 이 한 줄이 양자화의 전부예요.

### 정수끼리 곱하고 마지막에 한 번만 되돌리기

양자화가 빨라지는 비밀은 **계산 자체를 정수로** 한다는 데 있습니다. 6장 6.1절의 층 하나, 즉 행렬 곱 `a @ w`를 정수로 해 보겠습니다.

```python
import torch

torch.manual_seed(0)
a = torch.rand(4, 64) * 3                         # 입력(활성값): 0 이상
w = torch.randn(64, 8) * 0.1                      # 가중치: 0 근처, 양수와 음수


def 양자화(x: torch.Tensor, 작은: int, 큰: int) -> tuple[torch.Tensor, float, int]:
    """x의 범위를 정수 작은~큰 눈금에 맞춘다 (19.8절의 비대칭 방식)."""
    lo, hi = min(x.min().item(), 0.0), max(x.max().item(), 0.0)
    배율 = (hi - lo) / (큰 - 작은)
    영점 = round(작은 - lo / 배율)
    return (x / 배율 + 영점).round().clamp(작은, 큰).to(torch.int32), 배율, 영점


qa, sa, za = 양자화(a, 0, 255)                     # 입력은 uint8
qw, sw, zw = 양자화(w, -128, 127)                  # 가중치는 int8
# 정수끼리 곱해 int32에 모으고, 마지막에 한 번만 배율을 곱해 실수로 되돌린다
정수_누적 = (qa - za) @ (qw - zw)                  # int32 행렬 곱
결과 = 정수_누적.float() * (sa * sw)

정답 = a @ w
print("정수 누적값의 자료형:", 정수_누적.dtype, "최댓값:", 정수_누적.abs().max().item())
print("실수 행렬 곱 :", 정답[0, :4])
print("정수 행렬 곱 :", 결과[0, :4])
print(f"상대 오차: {((결과 - 정답).norm() / 정답.norm()).item():.4f}")
```

```text
정수 누적값의 자료형: torch.int32 최댓값: 177979
실수 행렬 곱 : tensor([-1.0971,  3.5936, -2.0597, -1.3047])
정수 행렬 곱 : tensor([-1.0872,  3.5964, -2.0531, -1.3087])
상대 오차: 0.0035
```

입력 `a`는 uint8로, 가중치 `w`는 int8로 바꿨습니다. 실수 하나는 `(정수 - 영점) × 배율`이니, 두 실수의 곱은 `(qa - za) × (qw - zw) × sa × sw`예요. 그런데 배율 `sa × sw`는 모든 칸에 같은 숫자라서 덧셈 밖으로 꺼낼 수 있습니다. 그래서 **정수끼리 곱하고 더하는 일을 먼저 다 하고**, 맨 마지막에 배율을 한 번만 곱하면 돼요.

곱해서 더한 값은 17만이 넘어서 int8에 담을 수 없으니, 32비트 정수(int32)에 모읍니다. 결과는 실수 행렬 곱과 상대 오차 0.35% 차이로 거의 같아요. CPU와 휴대폰 칩, GPU에는 이런 8비트 정수 곱셈을 float32보다 몇 배 많이 한꺼번에 하는 명령이 있습니다. 읽어 올 숫자도 4분의 1로 줄고요. 양자화가 크기와 속도를 함께 줄일 수 있는 이유입니다.

### 배율을 얼마나 잘게 둘까

14장에서 int4가 망가진 것은 행마다 배율을 하나만 썼기 때문이라고 했습니다. 배율을 두는 단위를 **텐서마다**(텐서 전체에 하나), **채널마다**(출력 채널이나 행마다 하나), **묶음마다**(숫자 몇십 개씩 하나)로 바꿔 가며 9.5절 CNN의 가중치를 양자화해 보겠습니다.

```python
import torch

from 배포도구 import 불러오기, 옷CNN


def 왕복(w: torch.Tensor, 비트: int, 묶음: str) -> tuple[torch.Tensor, int]:
    """대칭 양자화했다가 되돌린 값과, 그때 쓴 배율의 개수."""
    최대 = 2 ** (비트 - 1) - 1
    if 묶음 == "텐서마다":
        조각 = w.reshape(1, -1)                     # 텐서 전체에 배율 하나
    elif 묶음 == "채널마다":
        조각 = w.reshape(w.shape[0], -1)            # 출력 채널(행)마다 하나
    else:
        조각 = w.reshape(-1, 32)                    # 숫자 32개마다 하나
    배율 = 조각.abs().amax(dim=1, keepdim=True) / 최대
    되돌림 = (조각 / 배율).round().clamp(-최대, 최대) * 배율
    return 되돌림.reshape(w.shape), 배율.numel()


모델 = 불러오기(옷CNN, "fashion_cnn.pt")
for 이름, w in [("합성곱 2층 (64, 32, 3, 3)", 모델.특징[3].weight.detach()),
                ("완전 연결 (128, 3136)", 모델.분류[1].weight.detach())]:
    print(이름)
    for 묶음 in ["텐서마다", "채널마다", "32개씩"]:
        오차 = []
        for 비트 in (8, 4):
            되돌림, 개수 = 왕복(w, 비트, 묶음)
            오차.append(((되돌림 - w).norm() / w.norm()).item())   # 상대 오차
        print(f"  {묶음:5} 배율 {개수:>6,}개   int8 오차 {오차[0]:.4f}   int4 오차 {오차[1]:.4f}")
```

```text
합성곱 2층 (64, 32, 3, 3)
  텐서마다  배율      1개   int8 오차 0.0120   int4 오차 0.2175
  채널마다  배율     64개   int8 오차 0.0084   int4 오차 0.1530
  32개씩  배율    576개   int8 오차 0.0058   int4 오차 0.1055
완전 연결 (128, 3136)
  텐서마다  배율      1개   int8 오차 0.0235   int4 오차 0.3642
  채널마다  배율    128개   int8 오차 0.0115   int4 오차 0.2077
  32개씩  배율 12,544개   int8 오차 0.0058   int4 오차 0.1057
```

배율을 잘게 둘수록 오차가 줄어듭니다. 큰 완전 연결층에서 int8은 텐서마다 2.35% → 채널마다 1.15% → 32개씩 0.58%, int4는 36.4% → 20.8% → 10.6%예요. 이유는 14장의 자 비유 그대로입니다. 행 하나에 아주 큰 값이 하나 있으면 그 행 전체의 눈금 간격이 넓어지는데, 묶음을 작게 나누면 큰 값의 영향이 그 묶음 안에만 머물러요.

대신 배율도 저장해야 합니다. 완전 연결층을 32개씩 나누면 배율이 12,544개가 생겨요. 배율을 float32로 저장하면 숫자 32개(int4로 16바이트)마다 4바이트가 더 붙는 셈입니다. 그래서 보통 int8은 **가중치는 채널마다, 활성값은 텐서마다** 배율을 두고, int4처럼 눈금이 거친 방식은 묶음마다 배율을 둬요. 14장의 LLM을 4비트로 줄이는 GPTQ, AWQ 같은 방법들은 여기에 더해 "오차가 덜 나도록 눈금에 맞추는 요령"을 쓰는 것입니다.

## 19.9 PyTorch 안에서 양자화하기: torchao

### 한 줄로 바꾸기

원리를 알았으니 도구를 써 보겠습니다. PyTorch 쪽 양자화 도구는 **torchao**예요. `quantize_` 함수에 모델과 설정을 넘기면, 모델 안의 `nn.Linear`를 제자리에서 양자화된 것으로 바꿉니다. 가중치만 int8로 담는 방식과, 입력(활성값)까지 실행할 때 int8로 바꿔 정수 계산을 하는 방식을 비교해 보겠습니다.

```python
import copy
import io

import torch
from torchao.quantization import (Int8DynamicActivationInt8WeightConfig, Int8WeightOnlyConfig,
                                  quantize_)

from 배포도구 import 불러오기, 시간_재기, 시험_데이터, 옷CNN

torch.set_num_threads(4)
X, y = 시험_데이터()
원본 = 불러오기(옷CNN, "fashion_cnn.pt")


def 저장_크기(모델: torch.nn.Module) -> float:
    """state_dict를 torch.save했을 때의 크기(KB). 파일 대신 메모리 버퍼에 써 본다."""
    버퍼 = io.BytesIO()
    torch.save(모델.state_dict(), 버퍼)
    return len(버퍼.getvalue()) / 1024


for 이름, 설정 in [("float32 (원본)", None),
                   ("가중치만 int8", Int8WeightOnlyConfig()),
                   ("가중치·입력 int8", Int8DynamicActivationInt8WeightConfig())]:
    모델 = copy.deepcopy(원본)
    if 설정 is not None:
        quantize_(모델, 설정)                      # 모델 안의 nn.Linear를 제자리에서 바꾼다
    with torch.inference_mode():
        정확도 = (모델(X).argmax(dim=1) == y).float().mean().item()
        한장 = 시간_재기(lambda: 모델(X[:1]))
        묶음 = 시간_재기(lambda: 모델(X[:64]))
    print(f"{이름}: {저장_크기(모델):,.0f}KB, 정확도 {정확도:.2%}, 1장 {한장:.3f}ms, 64장 {묶음:.3f}ms")

w = 모델.분류[1].weight                            # 마지막으로 바꾼 모델의 큰 Linear
print(type(w).__name__, "정수:", w.qdata.dtype, tuple(w.qdata.shape),
      "배율:", tuple(w.scale.shape))
```

```text
float32 (원본): 1,650KB, 정확도 91.01%, 1장 0.114ms, 64장 3.490ms
가중치만 int8: 472KB, 정확도 91.02%, 1장 0.198ms, 64장 3.590ms
가중치·입력 int8: 473KB, 정확도 90.98%, 1장 0.288ms, 64장 3.808ms
Int8Tensor 정수: torch.int8 (128, 3136) 배율: (128, 1)
```

크기는 1,650KB에서 472KB로 3.5배쯤 줄었고, 정확도는 91.01%에서 91.02%, 90.98%로 사실상 그대로입니다. 4배가 아닌 이유는 합성곱층은 바꾸지 않았기 때문이에요(`quantize_`는 기본으로 `nn.Linear`만 바꿉니다). 9장 9.5절에서 본 대로 이 모델은 큰 `Linear` 하나가 파라미터의 95%를 차지하니 거의 다 줄어든 셈이죠. 마지막 줄을 보면 그 `Linear`의 가중치가 `Int8Tensor`로 바뀌었고, 안에 int8 정수 (128, 3136)와 **행마다 하나씩인** 배율 (128, 1)을 갖고 있습니다. 앞 절의 "채널마다" 방식이에요.

그런데 속도는 오히려 **느려졌습니다.** 이 맥의 CPU에서 PyTorch를 그대로 실행하는 방식으로는, 정수 칸의 가중치를 다루는 추가 작업이 정수 계산으로 아낀 시간보다 컸던 거예요. 14장 14.6절 Q&A에서 "양자화하면 빨라지는가는 장비와 방법에 따라 다르다"고 했던 것을 실제로 확인한 셈입니다. 크기와 메모리는 확실히 줄었으니, 메모리가 모자라 모델이 안 들어가는 상황이라면 이것만으로도 쓸모가 있어요. 속도까지 얻으려면 그 장비에서 빠른 정수 계산을 쓰는 실행 방식이 함께 필요합니다. 다음 절의 ONNX Runtime이 그 예입니다.

> **Q. 다른 책에서는 `torch.ao.quantization.quantize_dynamic`을 쓰던데요?**
> PyTorch에 예전부터 있던 양자화 도구입니다. PyTorch 2.14에도 남아 있지만, 쓰면 "`torch.ao.quantization`은 더 이상 권하지 않으며 torchao의 `quantize_`로 옮기라"는 경고가 나와요. 맥에서는 `torch.backends.quantized.engine = "qnnpack"`을 먼저 설정해야 동작하는 등 손도 많이 갑니다. 새로 짜는 코드라면 torchao를 쓰세요.

## 19.10 ONNX Runtime으로 양자화하기

### 동적 양자화

ONNX Runtime에도 양자화 도구가 들어 있습니다. ONNX 파일을 받아 양자화된 ONNX 파일을 내놓으니, 내보내기가 끝난 뒤의 마지막 단계로 쓰기 좋아요. 먼저 **동적 양자화(dynamic quantization)** 입니다. 가중치는 미리 int8로 바꿔 저장하고, 활성값은 실행할 때마다 그 입력을 보고 배율과 영점을 그때그때 정해요.

```python
from collections import Counter

import onnx
from onnxruntime.quantization import QuantType, quantize_dynamic
from onnxruntime.quantization.shape_inference import quant_pre_process

from 배포도구 import (ONNX로_내보내기, 불러오기, 세션_만들기, 세션_정확도, 시간_재기,
                     시험_데이터, 옷CNN, 파일_크기)

ONNX로_내보내기(불러오기(옷CNN, "fashion_cnn.pt"), "fashion_cnn.onnx")
quant_pre_process("fashion_cnn.onnx", "fashion_cnn_pre.onnx")          # 양자화 전 준비(모양 추론 등)
quantize_dynamic("fashion_cnn_pre.onnx", "fashion_cnn_dynamic.onnx",
                 weight_type=QuantType.QInt8)                           # 가중치를 int8로

X, y = 시험_데이터()
X, y = X.numpy(), y.numpy()
for 경로 in ["fashion_cnn.onnx", "fashion_cnn_dynamic.onnx"]:
    세션 = 세션_만들기(경로)
    print(f"{경로:26} {파일_크기(경로):7.1f}KB  정확도 {세션_정확도(세션, X, y):.2%}  "
          f"64장 {시간_재기(lambda: 세션.run(None, {'사진': X[:64]})):.3f}ms")
연산 = Counter(노드.op_type for 노드 in onnx.load("fashion_cnn_dynamic.onnx").graph.node)
print(dict(연산.most_common()))
```

```text
fashion_cnn.onnx            1662.5KB  정확도 91.01%  64장 1.652ms
fashion_cnn_dynamic.onnx     425.1KB  정확도 91.03%  64장 2.683ms
{'Mul': 8, 'DynamicQuantizeLinear': 4, 'Cast': 4, 'Add': 4, 'Reshape': 3, 'Relu': 3, 'ConvInteger': 2, 'MaxPool': 2, 'MatMulInteger': 2}
```

`quant_pre_process`는 양자화 전에 그래프를 정리하고 각 값의 모양을 적어 두는 준비 단계입니다. ONNX Runtime 문서가 양자화 전에 해 두기를 권하는 단계예요. 결과를 보면 크기가 1,662KB에서 425KB로 4분의 1이 됐고, 정확도는 91.03%로 그대로입니다.

그런데 64장 묶음의 시간이 1.7ms에서 2.7ms로 **늘었습니다.** 맨 아래 연산자 목록이 이유를 말해 줘요. `DynamicQuantizeLinear`가 실행할 때마다 활성값의 최솟값·최댓값을 찾아 배율과 영점을 계산하고, `ConvInteger`, `MatMulInteger`가 정수 계산을 한 뒤, `Cast`, `Mul`, `Add`로 다시 실수로 되돌립니다. 층마다 이 앞뒤 작업이 붙으니 작은 CNN에서는 정수 계산으로 아낀 것보다 더 들었어요. ONNX Runtime 문서도 동적 양자화는 RNN이나 트랜스포머 계열 모델에, 정적 양자화는 CNN에 권합니다. 트랜스포머는 거대한 행렬 곱(`MatMul`)이 대부분이라 가중치를 읽는 시간이 크게 줄어드는 이득이 앞뒤 작업보다 크거든요.

### 정적 양자화와 보정 데이터

**정적 양자화(static quantization)** 는 활성값의 배율과 영점도 **미리 정해** 둡니다. 실행할 때 계산하지 않으니 앞뒤 작업이 줄어들죠. 그런데 미리 정하려면 "층마다 활성값이 대개 어느 범위에 있는지"를 알아야 해요. 그래서 실제 입력과 닮은 사진을 조금 흘려보내 범위를 재는데, 이 과정을 **보정(calibration)**, 그 사진들을 **보정 데이터**라고 합니다. 시험 전에 모의고사를 몇 번 쳐 보고 점수 분포를 보는 것과 비슷해요.

```python
from collections import Counter

import numpy as np
import onnx
from onnxruntime.quantization import (CalibrationDataReader, QuantFormat, QuantType,
                                      quantize_static)
from onnxruntime.quantization.shape_inference import quant_pre_process
from torchvision import datasets

from 배포도구 import (ONNX로_내보내기, 불러오기, 세션_만들기, 세션_정확도, 시간_재기,
                     시험_데이터, 옷CNN, 파일_크기)


class 보정_데이터(CalibrationDataReader):
    """보정용 사진 묶음을 32장씩 하나씩 건네주는 읽개."""

    def __init__(self, 사진: np.ndarray, 크기: int = 32) -> None:
        self.묶음들 = iter([{"사진": 사진[i:i + 크기]} for i in range(0, len(사진), 크기)])

    def get_next(self) -> dict[str, np.ndarray] | None:
        return next(self.묶음들, None)              # 다 건네면 None


# 보정에는 시험 데이터가 아니라 학습 데이터의 일부를 쓴다
학습셋 = datasets.FashionMNIST("data", train=True, download=True)
보정용 = (학습셋.data[:512].float().unsqueeze(1) / 255).numpy()

ONNX로_내보내기(불러오기(옷CNN, "fashion_cnn.pt"), "fashion_cnn.onnx")
quant_pre_process("fashion_cnn.onnx", "fashion_cnn_pre.onnx")
quantize_static("fashion_cnn_pre.onnx", "fashion_cnn_static.onnx", 보정_데이터(보정용),
                quant_format=QuantFormat.QDQ, per_channel=True,
                activation_type=QuantType.QUInt8, weight_type=QuantType.QInt8)

X, y = 시험_데이터()
X, y = X.numpy(), y.numpy()
for 경로 in ["fashion_cnn.onnx", "fashion_cnn_static.onnx"]:
    세션 = 세션_만들기(경로)
    print(f"{경로:24} {파일_크기(경로):7.1f}KB  정확도 {세션_정확도(세션, X, y):.2%}  "
          f"1장 {시간_재기(lambda: 세션.run(None, {'사진': X[:1]})):.3f}ms  "
          f"64장 {시간_재기(lambda: 세션.run(None, {'사진': X[:64]})):.3f}ms")
연산 = Counter(노드.op_type for 노드 in onnx.load("fashion_cnn_static.onnx").graph.node)
print(dict(연산.most_common()))
```

```text
fashion_cnn.onnx          1662.5KB  정확도 91.01%  1장 0.067ms  64장 2.146ms
fashion_cnn_static.onnx    430.7KB  정확도 91.09%  1장 0.026ms  64장 0.994ms
{'DequantizeLinear': 16, 'QuantizeLinear': 8, 'Conv': 2, 'MaxPool': 2, 'Gemm': 2, 'Reshape': 1}
```

보정 데이터는 `CalibrationDataReader`를 이어받은 클래스로 건넵니다. `get_next`가 부를 때마다 `{입력 이름: 묶음}`을 하나씩 돌려주고, 다 주면 `None`을 돌려주면 돼요. 1권 15장의 반복자와 같은 생각입니다. 보정에는 학습 데이터의 512장을 썼어요. **시험 데이터로 보정하면 안 됩니다.** 보정도 데이터를 보고 숫자를 정하는 일이니, 시험 데이터를 쓰면 2장 2.3절의 데이터 누수가 돼요.

결과가 좋습니다. 크기는 431KB로 동적 양자화와 비슷하게 4분의 1이 됐고, 정확도는 91.09%로 원본(91.01%)과 거의 같으며, 시간은 사진 1장이 0.067ms에서 0.026ms로, 64장이 2.1ms에서 1.0ms로 **줄었습니다.**

연산자 목록에는 `QuantizeLinear`와 `DequantizeLinear`가 짝지어 있고, 가운데의 `Conv`, `Gemm`은 원래 이름 그대로입니다. 이런 모양을 **QDQ 형식**이라고 해요. "여기서 정수로 바꿨다가(Q) 다시 실수로 되돌린다(DQ)"는 표시만 그래프에 붙여 두는 방식인데, 19.6절에서 본 ONNX Runtime의 그래프 다듬기가 세션을 만들 때 이 표시를 보고 `DQ → Conv → Q` 묶음을 **정수 합성곱 하나**로 합칩니다. 표시만 붙인 그래프라 다른 런타임도 이해하기 쉬워서, ONNX Runtime이 기본으로 쓰는 형식이에요. `per_channel=True`는 19.8절의 "가중치는 채널마다" 배율을 쓰라는 옵션입니다. `activation_type=QuantType.QUInt8`과 `weight_type=QuantType.QInt8`은 19.8절에서 본 대로 활성값은 0~255 눈금(uint8)과 영점으로, 가중치는 int8로 담으라는 뜻이에요. 활성값 쪽을 적지 않으면 ONNX Runtime은 활성값도 int8로 담으니, 이 장의 뒤쪽 예제에서도 두 옵션을 그대로 적어 둡니다.

### 보정 데이터를 잘못 고르면

보정 데이터는 얼마나, 어떤 것을 써야 할까요? 이번에는 작은 ResNet으로 보정 데이터를 바꿔 가며 실험해 보겠습니다.

```python
import numpy as np
from onnxruntime.quantization import (CalibrationDataReader, QuantFormat, QuantType,
                                      quantize_static)
from onnxruntime.quantization.shape_inference import quant_pre_process
from torchvision import datasets

from 배포도구 import ONNX로_내보내기, 불러오기, 세션_만들기, 세션_정확도, 시험_데이터, 작은_ResNet


class 보정_데이터(CalibrationDataReader):
    """19.10절과 같은 읽개."""

    def __init__(self, 사진: np.ndarray, 크기: int = 32) -> None:
        self.묶음들 = iter([{"사진": 사진[i:i + 크기]} for i in range(0, len(사진), 크기)])

    def get_next(self) -> dict[str, np.ndarray] | None:
        return next(self.묶음들, None)


학습셋 = datasets.FashionMNIST("data", train=True, download=True)
진짜 = (학습셋.data[:512].float().unsqueeze(1) / 255).numpy()
보정_후보 = {
    "학습 사진 512장": 진짜,
    "학습 사진 8장": 진짜[:8],
    "새까만 사진 64장": np.zeros_like(진짜[:64]),
    "0~255 그대로 64장": 진짜[:64] * 255,         # 전처리(/255)를 빼먹은 실수
}

ONNX로_내보내기(불러오기(작은_ResNet, "fashion_resnet.pt"), "fashion_resnet.onnx")
quant_pre_process("fashion_resnet.onnx", "fashion_resnet_pre.onnx")
X, y = 시험_데이터()
X, y = X.numpy(), y.numpy()
print(f"float32 원본: 정확도 {세션_정확도(세션_만들기('fashion_resnet.onnx'), X, y):.2%}")
for 이름, 사진 in 보정_후보.items():
    quantize_static("fashion_resnet_pre.onnx", "fashion_resnet_calib.onnx", 보정_데이터(사진),
                    quant_format=QuantFormat.QDQ, per_channel=True,
                    activation_type=QuantType.QUInt8, weight_type=QuantType.QInt8)
    정확도 = 세션_정확도(세션_만들기("fashion_resnet_calib.onnx"), X, y)
    print(f"[{이름}] 보정 후 정확도 {정확도:.2%}")
```

```text
float32 원본: 정확도 93.04%
[학습 사진 512장] 보정 후 정확도 93.07%
[학습 사진 8장] 보정 후 정확도 92.98%
[새까만 사진 64장] 보정 후 정확도 54.86%
[0~255 그대로 64장] 보정 후 정확도 9.85%
```

학습 사진 512장으로 보정하면 93.07%로 원본(93.04%)과 같고, **8장**만으로도 92.98%입니다. 활성값의 범위만 재면 되니 많이 필요하지 않아요. 문제는 데이터의 **종류**입니다. 새까만 사진으로 보정하면 54.86%로 무너지고, `/ 255`를 빼먹어 0~255 값을 그대로 넣으면 9.85%, 열 가지 중 찍는 수준이 됩니다. 범위를 엉뚱하게 재면 실제 입력이 눈금 밖으로 나가 잘려 버리거나, 눈금이 너무 거칠어지기 때문이에요.

무서운 점은 이 과정에서 **오류가 하나도 나지 않는다**는 것입니다. 양자화는 조용히 끝나고, 정확도를 재 봐야 비로소 알 수 있어요. 그래서 양자화 뒤에는 반드시 원본과 같은 시험 데이터로 정확도를 비교해야 합니다. 그리고 19.3절에서 말한 전처리 이야기가 여기서도 그대로예요. 보정 데이터도, 배포 후의 입력도 **학습 때와 똑같이 전처리**해야 합니다.

## 19.11 더 작게 만드는 다른 방법: 가지치기와 지식 증류

양자화는 "숫자 하나를 담는 칸"을 줄였습니다. 모델을 작게 만드는 길은 두 가지가 더 있어요. 숫자의 **개수**를 줄이는 가지치기와, **작은 모델을 새로 가르치는** 지식 증류입니다. 둘 다 깊이 들어가면 한 장씩 필요한 주제라, 아이디어만 실험으로 확인하겠습니다.

### 가지치기: 작은 가중치를 0으로

정원사가 웃자란 가지를 쳐내듯, **가지치기(pruning)** 는 절댓값이 작은 가중치를 0으로 만듭니다. 0에 가까운 가중치는 결과에 거의 기여하지 않을 테니까요. PyTorch에는 `torch.nn.utils.prune`이 있습니다.

```python
import gzip
import io

import torch
import torch.nn.utils.prune as prune

from 배포도구 import 불러오기, 시험_데이터, 옷CNN

X, y = 시험_데이터()


def 크기들(모델: torch.nn.Module) -> tuple[float, float]:
    """state_dict의 저장 크기와 gzip으로 압축한 크기(KB)."""
    버퍼 = io.BytesIO()
    torch.save(모델.state_dict(), 버퍼)
    return len(버퍼.getvalue()) / 1024, len(gzip.compress(버퍼.getvalue())) / 1024


for 비율 in [0.0, 0.5, 0.8, 0.9]:
    모델 = 불러오기(옷CNN, "fashion_cnn.pt")
    대상 = [(모델.특징[0], "weight"), (모델.특징[3], "weight"),
            (모델.분류[1], "weight"), (모델.분류[3], "weight")]
    if 비율 > 0:
        # 네 층의 가중치를 한데 모아 절댓값이 작은 것부터 '비율'만큼 0으로
        prune.global_unstructured(대상, pruning_method=prune.L1Unstructured, amount=비율)
        for 층, 이름 in 대상:
            prune.remove(층, 이름)                  # 가림판을 떼고 0을 가중치에 굳힌다
    영 = sum((층.weight == 0).sum().item() for 층, _ in 대상)
    전체 = sum(층.weight.numel() for 층, _ in 대상)
    with torch.no_grad():
        정확도 = (모델(X).argmax(dim=1) == y).float().mean().item()
    저장, 압축 = 크기들(모델)
    print(f"가지치기 {비율:3.0%}: 0인 가중치 {영 / 전체:5.1%}, 정확도 {정확도:.2%}, "
          f"저장 {저장:,.0f}KB, gzip {압축:,.0f}KB")
```

```text
가지치기  0%: 0인 가중치  0.0%, 정확도 91.01%, 저장 1,650KB, gzip 1,532KB
가지치기 50%: 0인 가중치 50.0%, 정확도 90.99%, 저장 1,650KB, gzip 894KB
가지치기 80%: 0인 가중치 80.0%, 정확도 89.37%, 저장 1,650KB, gzip 447KB
가지치기 90%: 0인 가중치 90.0%, 정확도 78.15%, 저장 1,650KB, gzip 283KB
```

`global_unstructured`는 네 층의 가중치를 한데 모아 절댓값이 작은 것부터 정한 비율만큼 0으로 만들고, `prune.remove`는 그 결과를 가중치에 굳힙니다. 가중치의 절반을 0으로 만들어도 정확도는 91.01%에서 90.99%로 그대로고, 80%를 0으로 만들어도 89.37%예요. 90%에서는 78.15%로 크게 떨어집니다.

그런데 **저장 크기가 1,650KB로 그대로**입니다. 0도 float32 숫자 하나라서 4바이트를 차지하거든요. 계산량도 그대로예요. 0을 곱하는 것도 곱셈이니까요. 대신 gzip으로 압축하면 50%에서 894KB, 80%에서 447KB로 줄어듭니다. 같은 0이 잔뜩 반복되니 압축이 잘 되는 거죠. 가지치기로 실제 속도를 얻으려면 0을 건너뛰는 특별한 계산 방식이나, 채널이나 필터를 **통째로** 잘라 내서 층 자체를 작게 만드는 방식이 필요합니다. 그래서 실무에서는 압축된 크기만 필요할 때 쓰거나, 통째로 잘라 낸 뒤 다시 조금 학습시키는 식으로 씁니다.

### 지식 증류: 선생의 답안지로 배우기

**지식 증류(knowledge distillation)** 는 큰 모델(선생)의 출력을 보고 작은 모델(학생)을 가르치는 방법입니다. 정답 레이블은 "이건 셔츠"라는 한 가지만 알려 주지만, 선생의 점수는 "셔츠일 확률 80%, T셔츠일 확률 17%"처럼 **무엇과 얼마나 닮았는지**까지 알려 주죠. 학생은 그 닮음의 정도까지 따라 배웁니다.

9.10절의 작은 ResNet(파라미터 308,074개)을 선생으로, 파라미터가 9,098개뿐인 작은 CNN을 학생으로 하겠습니다. 학생에게는 학습 사진 **2,000장**만 주고, 정답만으로 배운 학생과 선생의 점수도 함께 따라 배운 학생을 씨앗 세 개로 비교해요(18장에서 다루는 "여러 씨앗으로 돌려 평균 내기"를 미리 해 보는 셈입니다).

```python
import torch
import torch.nn.functional as F
from torch import nn
from torchvision import datasets

from 배포도구 import 불러오기, 시험_데이터, 작은_ResNet

torch.set_num_threads(4)
학습셋 = datasets.FashionMNIST("data", train=True, download=True)
X학습 = 학습셋.data[:2000].float().unsqueeze(1) / 255      # 학생에게는 2,000장만
y학습 = 학습셋.targets[:2000]
X, y = 시험_데이터()

선생 = 불러오기(작은_ResNet, "fashion_resnet.pt")          # 6만 장으로 배운 선생 (308,074개)
with torch.no_grad():
    선생_점수 = 선생(X학습)                                  # 선생의 답안지를 미리 받아 둔다


def 학생() -> nn.Sequential:
    """채널을 확 줄인 작은 CNN."""
    return nn.Sequential(
        nn.Conv2d(1, 8, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        nn.Conv2d(8, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        nn.Flatten(), nn.Linear(16 * 7 * 7, 10),
    )


def 학습시키기(증류: bool, 씨앗: int, 온도: float = 4.0, 비중: float = 0.9) -> float:
    """학생을 30에폭 학습하고 시험 정확도를 돌려준다. 증류면 선생의 점수도 따라 배운다."""
    torch.manual_seed(씨앗)
    모델 = 학생()
    옵티마이저 = torch.optim.Adam(모델.parameters(), lr=2e-3)
    for _ in range(30):
        for 번호 in torch.randperm(2000).split(64):
            출력 = 모델(X학습[번호])
            손실 = F.cross_entropy(출력, y학습[번호])
            if 증류:   # 온도로 부드럽게 만든 두 확률 분포의 차이 (KL 발산)
                따라하기 = F.kl_div(F.log_softmax(출력 / 온도, dim=1),
                                    F.softmax(선생_점수[번호] / 온도, dim=1),
                                    reduction="batchmean") * 온도 ** 2
                손실 = 비중 * 따라하기 + (1 - 비중) * 손실
            옵티마이저.zero_grad()
            손실.backward()
            옵티마이저.step()
    with torch.no_grad():
        return (모델(X).argmax(dim=1) == y).float().mean().item()


print(f"학생 파라미터 {sum(p.numel() for p in 학생().parameters()):,}개")
결과 = {"정답만": [], "증류": []}
for 씨앗 in range(3):
    for 방식 in 결과:
        결과[방식].append(학습시키기(방식 == "증류", 씨앗))
for 방식, 값 in 결과.items():
    print(f"{방식:4}: " + ", ".join(f"{v:.2%}" for v in 값) + f"  평균 {sum(값) / len(값):.2%}")
```

```text
학생 파라미터 9,098개
정답만 : 84.21%, 83.60%, 82.23%  평균 83.35%
증류  : 85.09%, 84.11%, 85.21%  평균 84.80%
```

세 씨앗 모두 증류한 학생이 더 높았고, 평균은 83.35%에서 84.80%로 1.45%p 올랐습니다. 학생은 같은 2,000장을 봤지만, 선생의 점수에는 선생이 6만 장에서 배운 "옷들이 서로 얼마나 닮았나"가 담겨 있어서 그것까지 전해 받은 거예요.

코드에서 두 가지를 보세요. 하나는 **온도**입니다. 14장 14.3절에서 온도로 확률 분포를 평평하게 만들었죠. 선생의 점수를 온도 4로 나눠 소프트맥스를 하면 1등이 아닌 클래스의 확률도 드러나서 닮음의 정도가 잘 보입니다. 다른 하나는 **손실을 섞는 비중**이에요. 선생 따라 하기(KL 발산)에 0.9, 정답 맞히기에 0.1을 줬습니다. 온도 제곱을 곱한 것은 온도로 나누면서 작아진 기울기 크기를 되돌리려는 관례예요.

정직하게 덧붙이면, 학생에게도 6만 장을 다 주고 3에폭씩 같은 비교를 했을 때는 증류의 이득이 보이지 않았습니다. 세 씨앗의 평균이 정답만 배운 학생 88.52%, 증류한 학생 87.60%로 오히려 조금 낮았어요. 데이터가 넉넉하면 학생이 정답만으로도 충분히 배우기 때문이에요. 증류는 학생이 볼 수 있는 레이블 데이터가 적거나, 선생이 학생보다 훨씬 많은 것을 알 때 빛납니다. 오늘날 작은 LLM 중 상당수가 큰 LLM을 선생으로 이런 방식의 학습을 거쳐 만들어져요.

## 19.12 휴대폰과 작은 기기에서: 런타임 고르기

ONNX Runtime은 실행 장치를 바꿔 끼울 수 있습니다. 19.3절에서 `providers=["CPUExecutionProvider"]`라고 쓴 자리예요. 이 컴퓨터에서 쓸 수 있는 것을 확인해 보겠습니다.

```python
import onnxruntime as ort

print("ONNX Runtime", ort.__version__)
print("이 컴퓨터에서 쓸 수 있는 실행 장치:", ort.get_available_providers())
```

```text
ONNX Runtime 1.31.0
이 컴퓨터에서 쓸 수 있는 실행 장치: ['CoreMLExecutionProvider', 'AzureExecutionProvider', 'CPUExecutionProvider']
```

이 맥에서는 CPU 말고도 `CoreMLExecutionProvider`가 보입니다. 애플 기기의 Core ML을 통해 GPU나 신경망 엔진을 쓰는 실행 장치예요. NVIDIA GPU가 있는 컴퓨터에 GPU용 ONNX Runtime을 설치하면 `CUDAExecutionProvider`가 나타납니다. 모델 파일은 그대로 두고 `providers` 목록만 바꾸면 된다는 것이 ONNX Runtime의 장점이에요. 다만 실행 장치마다 지원하는 연산과 속도가 다르니, 바꿨다면 19.3절처럼 결과를 비교하고 19.7절처럼 시간을 다시 재야 합니다.

휴대폰이나 작은 기기에서 돌릴 때는 런타임 선택지가 더 있습니다. 이름과 한 줄 소개만 정리해 둘게요.

| 런타임 | 한 줄 소개 |
|---|---|
| ONNX Runtime (모바일·웹) | 이 장에서 쓴 엔진의 안드로이드·iOS판과 웹 브라우저판. ONNX 파일을 그대로 쓴다 |
| ExecuTorch | PyTorch가 만든 기기용 런타임. `torch.export`로 딴 그래프를 기기용 파일로 바꿔 돌린다 |
| LiteRT | 구글의 기기용 런타임. 예전 이름은 TensorFlow Lite |
| Core ML | 애플 기기의 머신러닝 프레임워크. coremltools로 PyTorch 모델을 바꿔 넣는다 |
| TensorRT | NVIDIA GPU용 추론 최적화 도구. ONNX 파일을 받아 그 GPU에 맞게 다듬는다 |
| OpenVINO | 인텔 CPU·GPU용 추론 도구. ONNX 파일을 읽을 수 있다 |

어느 것을 고를지는 결국 **어디서 돌릴 것인가**가 정합니다. 파이썬 서버나 여러 운영체제를 함께 지원해야 한다면 ONNX Runtime이 무난하고, 특정 기기나 가속기의 성능을 끝까지 뽑아야 한다면 그 회사의 도구를 씁니다. 어느 쪽이든 이 장에서 익힌 과정, 즉 **내보내기 → 같은 답인지 확인 → 양자화 → 정확도와 시간 다시 재기**는 똑같아요.

## 19.13 실습: 작은 ResNet을 배포용으로 만들기

### 내보내고, 양자화하고, 같은 잣대로 비교하기

이 장에서 배운 것을 모아 9장 9.10절의 작은 ResNet을 배포용 파일로 만들겠습니다. 할 일은 세 가지예요.

1. ONNX로 내보내고 PyTorch와 같은 답을 내는지 확인하기
2. 학습 사진 512장으로 보정해 정적 양자화하기(가중치는 int8·채널마다 배율, 활성값은 uint8, QDQ 형식)
3. PyTorch float32, ONNX float32, ONNX int8을 **같은 잣대**로 비교하기: 파일 크기, 시험 정확도, 셔츠 정확도(9장의 약점), float32 PyTorch와 답이 같은 비율, 4칸 밀었을 때 정확도(9장 9.6절), 1장·64장 시간

```python
import numpy as np
import torch
from onnxruntime.quantization import (CalibrationDataReader, QuantFormat, QuantType,
                                      quantize_static)
from onnxruntime.quantization.shape_inference import quant_pre_process
from torchvision import datasets

from 배포도구 import (ONNX로_내보내기, 불러오기, 세션_만들기, 시간_재기, 시험_데이터,
                     작은_ResNet, 파일_크기)
from 옷도구 import 오른쪽으로_밀기


class 보정_데이터(CalibrationDataReader):
    """19.10절과 같은 읽개."""

    def __init__(self, 사진: np.ndarray, 크기: int = 32) -> None:
        self.묶음들 = iter([{"사진": 사진[i:i + 크기]} for i in range(0, len(사진), 크기)])

    def get_next(self) -> dict[str, np.ndarray] | None:
        return next(self.묶음들, None)


torch.set_num_threads(4)
X, y = 시험_데이터()
X_np, y_np = X.numpy(), y.numpy()
밀린_np = 오른쪽으로_밀기(X, 4).numpy()                 # 4칸 밀어 본 시험 사진

# 1) 내보내고 확인하기
모델 = 불러오기(작은_ResNet, "fashion_resnet.pt")
ONNX로_내보내기(모델, "fashion_resnet.onnx")
with torch.inference_mode():
    기준 = 모델(X).numpy()
원본 = 세션_만들기("fashion_resnet.onnx")
print(f"[확인] PyTorch와 최대 차이 {np.abs(원본.run(None, {'사진': X_np})[0] - 기준).max():.1e}")

# 2) 학습 사진 512장으로 보정해 정적 양자화
학습셋 = datasets.FashionMNIST("data", train=True, download=True)
보정용 = (학습셋.data[:512].float().unsqueeze(1) / 255).numpy()
quant_pre_process("fashion_resnet.onnx", "fashion_resnet_pre.onnx")
quantize_static("fashion_resnet_pre.onnx", "fashion_resnet_int8.onnx", 보정_데이터(보정용),
                quant_format=QuantFormat.QDQ, per_channel=True,
                activation_type=QuantType.QUInt8, weight_type=QuantType.QInt8)
정수 = 세션_만들기("fashion_resnet_int8.onnx")

# 3) 세 가지 실행 방법을 같은 잣대로 비교
후보 = {
    "PyTorch float32": ("fashion_resnet.pt", lambda x: 모델(torch.from_numpy(x)).numpy()),
    "ONNX float32": ("fashion_resnet.onnx", lambda x: 원본.run(None, {"사진": x})[0]),
    "ONNX int8": ("fashion_resnet_int8.onnx", lambda x: 정수.run(None, {"사진": x})[0]),
}
print(f"{'방법':16}{'크기':>8}{'정확도':>8}{'셔츠':>7}{'일치':>8}{'4칸':>7}{'1장':>9}{'64장':>9}")
for 이름, (파일, 실행) in 후보.items():
    with torch.inference_mode():
        예측 = 실행(X_np).argmax(axis=1)
        밀림 = (실행(밀린_np).argmax(axis=1) == y_np).mean()
        한장 = 시간_재기(lambda: 실행(X_np[:1]))
        묶음 = 시간_재기(lambda: 실행(X_np[:64]))
    셔츠 = (예측[y_np == 6] == 6).mean()
    일치 = (예측 == 기준.argmax(axis=1)).mean()             # float32 PyTorch와 같은 답의 비율
    print(f"{이름:16}{파일_크기(파일):6.0f}KB{(예측 == y_np).mean():8.2%}{셔츠:7.1%}"
          f"{일치:8.2%}{밀림:7.1%}{한장:7.3f}ms{묶음:7.2f}ms")
```

```text
[확인] PyTorch와 최대 차이 1.9e-05
방법                    크기     정확도     셔츠      일치     4칸       1장      64장
PyTorch float32   1227KB  93.04%  77.4% 100.00%  92.0%  0.586ms  36.73ms
ONNX float32      1235KB  93.04%  77.4% 100.00%  92.0%  0.278ms  15.09ms
ONNX int8          349KB  93.07%  77.2%  99.55%  92.0%  0.129ms   5.52ms
```

표를 한 칸씩 읽어 보겠습니다.

- **크기**: int8 모델은 349KB로 원본(1,227KB)의 4분의 1이 조금 넘습니다. 정확히 4분의 1이 아닌 것은 배율과 영점, 그리고 QDQ 표시 노드가 함께 들어 있기 때문이에요.
- **정확도**: 93.04% → 93.07%. 양자화로 잃은 것이 없습니다. 셔츠 정확도도 77.4%에서 77.2%로 거의 같고, 4칸 밀었을 때도 셋 다 92.0%예요. 9장에서 얻은 성질이 양자화 뒤에도 그대로 남았습니다.
- **일치**: 정확도가 같다고 답까지 다 같은 것은 아닙니다. int8 모델은 float32와 99.55%의 사진에서 같은 답을 냈어요. 1만 장 중 45장은 답이 바뀌었는데, 맞던 것이 틀리게 된 것과 틀리던 것이 맞게 된 것이 비슷해서 정확도는 그대로인 거죠. 경계에 걸친 애매한 사진들입니다. 실무에서 양자화를 검증할 때는 정확도와 함께 이 일치율도 보면 좋아요.
- **시간**: 이 책의 실행 환경(Apple M4 Max, CPU, 스레드 4개)에서 ONNX float32가 PyTorch보다 두 배 남짓 빠르고(19.7절과 같은 흐름이에요), int8은 거기서 다시 2~3배 빨라졌습니다. PyTorch와 견주면 1장은 4.5배, 64장은 6.7배 빠른 셈이에요. 다만 이 표는 컴퓨터가 한가할 때 잰 것입니다. 다른 프로그램이 CPU를 많이 쓰던 때 같은 실습을 돌렸더니 64장 시간이 PyTorch 101ms, ONNX float32 26ms, int8 7.7ms까지 늘었어요. 한가할 때 세 번 더 돌려 보면 PyTorch는 36~38ms, ONNX Runtime은 15ms 남짓, int8은 4.9~5.5ms로 거의 일정했습니다. 그래서 "몇 배 빨라졌다"는 숫자 하나보다, **같은 시각에 같은 잣대로 나란히 잰 표**와 그 흔들림의 폭을 함께 남기는 것이 정직한 보고입니다. 어느 실행에서든 순서는 같았어요. int8 ONNX가 가장 빠르고, PyTorch가 가장 느렸습니다.

### 배포하는 쪽의 코드

마지막으로, 이 파일을 받은 쪽에서 쓸 코드를 짜 보겠습니다. torch 없이, 넘파이와 ONNX Runtime만으로 0~255 정수 사진을 받아 확률 높은 후보 세 개를 돌려주는 작은 클래스예요. 전처리(`/ 255`)와 소프트맥스(6장 6.2절)를 직접 넣었습니다.

```python
import sys

import numpy as np
import onnxruntime as ort

이름 = ["T셔츠", "바지", "풀오버", "드레스", "코트", "샌들", "셔츠", "운동화", "가방", "앵클부츠"]


class 옷_분류기:
    """ONNX 파일 하나와 넘파이만으로 옷 사진을 분류한다 (torch 없이)."""

    def __init__(self, 경로: str) -> None:
        설정 = ort.SessionOptions()
        설정.intra_op_num_threads = 4
        self.세션 = ort.InferenceSession(경로, 설정, providers=["CPUExecutionProvider"])

    def 예측(self, 사진: np.ndarray, 몇_개: int = 3) -> list[list[tuple[str, float]]]:
        """0~255 정수 사진 (장 수, 28, 28)을 받아 장마다 확률 높은 순서로 몇_개를 돌려준다."""
        x = 사진.reshape(-1, 1, 28, 28).astype(np.float32) / 255     # 학습 때와 같은 전처리
        점수 = self.세션.run(None, {"사진": x})[0]
        확률 = np.exp(점수 - 점수.max(axis=1, keepdims=True))         # 소프트맥스 (6장 6.2절)
        확률 /= 확률.sum(axis=1, keepdims=True)
        순서 = np.argsort(-확률, axis=1)[:, :몇_개]
        return [[(이름[k], float(p[k])) for k in 줄] for p, 줄 in zip(확률, 순서)]


사진 = np.fromfile("data/FashionMNIST/raw/t10k-images-idx3-ubyte", dtype=np.uint8, offset=16)
정답 = np.fromfile("data/FashionMNIST/raw/t10k-labels-idx1-ubyte", dtype=np.uint8, offset=8)
사진 = 사진.reshape(-1, 28, 28)

분류기 = 옷_분류기("fashion_resnet_int8.onnx")
for 번호, 후보 in zip([0, 4, 7], 분류기.예측(사진[[0, 4, 7]])):
    print(f"{번호}번 (정답 {이름[정답[번호]]}): " + ", ".join(f"{n} {p:.1%}" for n, p in 후보))
print("torch를 불러왔나:", "torch" in sys.modules)
```

```text
0번 (정답 앵클부츠): 앵클부츠 99.9%, 운동화 0.1%, 샌들 0.0%
4번 (정답 셔츠): 셔츠 80.3%, T셔츠 17.4%, 코트 1.4%
7번 (정답 셔츠): 셔츠 99.8%, 코트 0.2%, 풀오버 0.0%
torch를 불러왔나: False
```

0번 사진은 앵클부츠를 99.9%로 확신했고, 7번 셔츠도 99.8%로 맞혔습니다. 눈여겨볼 것은 4번 사진이에요. 정답은 셔츠인데 셔츠 80.3%, T셔츠 17.4%로 나눠 걸었습니다. 9장 내내 이 모델을 괴롭힌 셔츠와 T셔츠의 혼동이 확률로 드러난 거예요. 앱에서는 이렇게 1등만 보여 주지 말고 확신이 낮을 때는 후보를 함께 보여 주는 식으로 쓸 수 있습니다. 마지막 줄의 `False`가 말해 주듯 이 코드는 PyTorch 없이 돌아갑니다. 앞에서 본 74MB짜리 ONNX Runtime과 349KB짜리 파일 하나면 충분해요.

## 19.14 정리와 다음 장 미리보기

이 장에서 모델을 PyTorch 밖으로 꺼내고 작게 줄였습니다.

- **ONNX**: 계산 그래프(노드) + 가중치(이니셜라이저) + 입출력 정보 + 연산자 판(opset)을 담는 공개 형식. pickle이 아니라 열 때 코드가 실행되지 않는다
- **내보내기**: `torch.onnx.export(모델, (예시_입력,), 경로)`. PyTorch 2.9부터 `torch.export` 기반이 기본. 평가 모드로, 작은 모델은 `external_data=False`로 한 파일에, `dynamic_shapes`로 묶음 차원 열기, `input_names`·`output_names`로 이름 붙이기
- **확인**: ONNX Runtime의 `InferenceSession`과 `run`(넘파이 배열을 주고받는다), PyTorch와 최대 차이 비교, 전처리는 배포하는 쪽에서 다시 짠다
- **내보낼 수 있는 코드**: `forward`는 텐서 연산만으로. 값에 따라 갈리는 `if`는 실패하니 `torch.where`나 `torch.cond`로, 파이썬 쪽 계산(넘파이 난수 등)은 상수로 굳는다
- **그래프 최적화**: 배치 정규화 접어 넣기, `Conv`·`Relu`·`Add` 합치기(`FusedConv`). 같은 모델이 ONNX Runtime에서 두 배쯤 빨랐다
- **속도 재기**: 준비 운동 뒤 여러 번 재서 중앙값, 스레드 수 맞추기, 실행 환경 밝히기
- **양자화 원리**: 실수 = (정수 - 영점) × 배율. 활성값은 uint8과 영점, 정수끼리 곱해 int32에 모으고 마지막에 배율 한 번. 배율은 텐서·채널·묶음마다, 잘게 둘수록 오차가 작다
- **양자화 도구**: torchao의 `quantize_`(크기는 줄었지만 이 CPU에서 빨라지지는 않음), ONNX Runtime의 동적 양자화(트랜스포머 계열에 알맞음)와 정적 양자화(CNN에 알맞음, 보정 데이터 필요, QDQ 형식). 보정 데이터는 학습 데이터에서, 학습 때와 같은 전처리로
- **그 밖의 방법**: 가지치기(0을 늘리지만 크기·속도는 그대로, 압축은 잘 됨), 지식 증류(선생의 점수로 작은 학생 가르치기)
- **실습 결과**: 작은 ResNet을 4분의 1 크기, 정확도 그대로, 이 책의 실행 환경에서 PyTorch보다 4~7배(1장 4.5배, 64장 6.7배) 빠른 파일로 만들었다. 시간은 같은 시각에 나란히 재고 흔들림의 폭도 함께 남긴다

모델이 파일 하나와 작은 런타임만으로 돌아가게 됐으니, 이제 이것을 다른 사람이 쓸 수 있게 열어 줄 차례입니다. 다음 20장에서는 1권 19장의 FastAPI 위에 모델을 올려 **웹 서비스**로 만들어요. 서버가 시작될 때 모델을 한 번만 불러오고, 업로드한 사진을 받아 분류하고, 여러 요청을 묶어 처리하고, 이 장에서 만든 ONNX 파일로 백엔드를 바꿔 끼운 뒤, Docker로 감싸 어디서든 띄울 수 있게 만듭니다.
