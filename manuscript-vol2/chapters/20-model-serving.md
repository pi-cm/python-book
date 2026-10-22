# Chapter 20. FastAPI로 모델 서빙: 내 모델을 웹 서비스로

> **학습 목표**  
> - 모델을 요청마다 불러오면 생기는 문제를 재 보고, `lifespan`으로 서버가 켜질 때 한 번만 올리기
> - Pydantic으로 추론 요청과 응답의 모양을 정하고, 업로드한 사진을 학습 때와 같은 방법으로 전처리하기
> - 여러 장을 한 번에 처리하는 배치 추론과, 따로 온 요청을 모아 한 번에 계산하는 방법 만들기
> - CPU를 오래 쓰는 추론이 이벤트 루프를 막는 모습을 보고, 스레드로 넘겨 해결하기
> - 헬스 체크·버전 정보·처리 시간 헤더를 달고, 지연 시간을 백분위수로 재기
> - 19장의 ONNX 파일로 백엔드를 바꿔 끼우고, LLM의 답을 토큰마다 흘려보내기
> - pytest로 서비스를 시험하고, uv와 Docker로 어디서나 같은 모습으로 띄우기

---

## 들어가며: 모델 파일을 친구에게 보내면 끝일까요?

9장에서 옷 사진을 91% 맞히는 CNN을 만들어 `fashion_cnn.pt`로 저장했습니다. 친구가 쇼핑 앱을 만드는데 "사진을 올리면 옷 종류를 자동으로 채워 주는 기능"에 이 모델을 쓰고 싶대요. 파일을 보내 주면 될까요?

19장 들어가며에서 본 것처럼 `.pt` 파일만으로는 아무것도 할 수 없습니다. 친구 앱에 파이썬과 PyTorch, 우리가 짠 `옷CNN` 클래스와 전처리 코드까지 옮겨야 하고, 모델을 고칠 때마다 친구 앱을 다시 배포해야 해요.

1권 19장의 식당을 떠올려 보세요. 손님은 주방에 들어가 요리하지 않습니다. 주문서를 내면 주방이 음식을 내줄 뿐이에요. 모델도 **주방에 두고 주문을 받으면** 됩니다. 친구 앱은 사진을 HTTP 요청에 담아 보내고, 우리 서버는 모델로 계산한 답을 JSON으로 돌려주는 거죠. 앱이 어떤 언어로 짜였든 HTTP만 보낼 줄 알면 되고, 모델을 바꿔도 서버만 다시 띄우면 됩니다. 이렇게 학습한 모델을 다른 프로그램이 쓸 수 있게 내놓는 일을 **모델 서빙(model serving)** 이라고 합니다.

경로 함수, `Depends`, Pydantic 검증, `TestClient`는 1권 19장에서 이미 써 봤어요. 그런데 주방에 들어오는 것이 블로그 글이 아니라 **모델**이 되면 새로운 고민이 생깁니다.

- 모델은 불러오는 데 오래 걸리고 메모리를 많이 씁니다. 언제 불러와 어디에 둘까요?
- 사진 파일을 학습할 때와 같은 모양으로 어떻게 바꿀까요?
- 추론이 CPU를 붙잡는 동안 다른 손님은 기다려야 할까요?
- 모아서 계산하면 빠른데 손님은 하나씩 옵니다. 어떻게 모을까요?
- 다른 컴퓨터에 옮겨도 똑같이 돌게 하려면 무엇을 챙길까요?

이 질문들에 하나씩 답한 뒤, 마지막 실습에서 9장 옷 분류기를 테스트까지 갖춘 서비스로 완성하고 Docker 이미지로 감쌉니다.

> **Q. 이 장에 필요한 패키지는 어떻게 설치하나요?**
> 프로젝트 폴더에서 `uv add "fastapi[standard]" pillow onnxruntime`을 실행하세요. `fastapi[standard]`에는 서버 `uvicorn`, 파일 업로드에 필요한 `python-multipart`, `TestClient`가 쓰는 HTTP 라이브러리가 함께 들어 있어요(1권 19.2절). `pillow`는 사진 파일을 여는 라이브러리, `onnxruntime`은 19장의 추론 엔진입니다. 20.10절은 14장의 `transformers`도 씁니다. 이 장의 예제는 파이썬 3.12, PyTorch 2.14.1, FastAPI 0.156.4, Pydantic 2.14.1, uvicorn 0.54.0, python-multipart 0.0.32, Pillow 13.0.0, ONNX Runtime 1.31.0, transformers 5.20.2, pytest 9.1.1에서 실행해 확인했고, 컨테이너는 Docker 28.3.2와 uv 0.9.16으로 만들었습니다.

## 20.1 모델을 서버에 올리기

### 이 장의 공통 도구

이 장의 예제는 거의 모두 9장 9.5절의 CNN을 불러와 씁니다. 9장의 `옷도구.py`에 들어 있는 설계도 `옷CNN`을 가져와서, 저장한 가중치를 **추론용으로** 불러오는 함수를 하나 만들어 두겠습니다. 아래 내용을 `서빙도구.py`로 저장하고, 같은 폴더에 9장의 `옷도구.py`와 `fashion_cnn.pt`를 두세요.

```python
"""20장 예제에서 함께 쓰는 도구: 9장 9.5절 CNN을 추론용으로 불러오기, 시험 사진을 파일로 만들기."""
import io
from pathlib import Path

import torch
from torchvision import datasets

from 옷도구 import 옷CNN

클래스_이름 = ["T셔츠", "바지", "풀오버", "드레스", "코트",
          "샌들", "셔츠", "운동화", "가방", "앵클부츠"]


def 모델_불러오기(경로: str | Path = "fashion_cnn.pt") -> 옷CNN:
    """저장된 가중치를 CPU로 불러와(4장 4.9절) 평가 모드로 돌려준다(6장 6.8절)."""
    모델 = 옷CNN()
    모델.load_state_dict(torch.load(경로, map_location="cpu", weights_only=True))
    return 모델.eval()


def 시험_사진_파일(개수: int) -> list[tuple[bytes, int]]:
    """FashionMNIST 시험 사진을 앞에서부터 개수만큼, PNG 파일 내용과 정답 번호로 돌려준다."""
    시험셋 = datasets.FashionMNIST("data", train=False, download=True)
    파일들 = []
    for i in range(개수):
        사진, 정답 = 시험셋[i]
        버퍼 = io.BytesIO()                       # 디스크 대신 메모리에 파일을 쓴다
        사진.save(버퍼, format="PNG")
        파일들.append((버퍼.getvalue(), 정답))
    return 파일들
```

`map_location="cpu"`는 GPU에서 저장한 파일도 CPU로 불러오게 하고(4장 4.9절), `weights_only=True`는 텐서 말고 다른 파이썬 객체가 든 파일을 거부합니다. 여러 사람이 쓰는 서버에서는 안전한 쪽이 기본이어야 해요. `.eval()`도 빠뜨리면 안 됩니다. 드롭아웃이나 배치 정규화가 있는 모델을 학습 모드로 서빙하면 같은 사진에도 답이 흔들리거나 정확도가 떨어져요(6장 6.8절).

### 요청마다 불러오면 생기는 일

가장 단순한 서빙은 경로 함수 안에서 모델을 불러와 계산하는 것입니다. 요리 주문이 들어올 때마다 주방을 새로 차리는 셈이죠. 미리 차려 둔 주방과 얼마나 차이가 날까요? 아직 사진 업로드를 만들지 않았으니, FashionMNIST 시험 사진의 **번호**를 주소로 받아 그 사진을 분류하는 API로 비교하겠습니다.

```python
import statistics
import time

import torch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from torchvision import datasets
from torchvision.transforms.functional import to_tensor

from 서빙도구 import 모델_불러오기, 클래스_이름

시험셋 = datasets.FashionMNIST("data", train=False, download=True)
app = FastAPI()
미리_올린_모델 = 모델_불러오기()             # 프로그램이 시작될 때 한 번


def 예측(모델: torch.nn.Module, index: int) -> dict:
    사진, 정답 = 시험셋[index]
    with torch.no_grad():
        점수 = 모델(to_tensor(사진).unsqueeze(0))
    return {"예측": 클래스_이름[점수.argmax().item()], "정답": 클래스_이름[정답]}


@app.get("/slow/{index}")
def 느린_예측(index: int) -> dict:
    return 예측(모델_불러오기(), index)       # 요청이 올 때마다 파일에서 다시 불러온다


@app.get("/fast/{index}")
def 빠른_예측(index: int) -> dict:
    return 예측(미리_올린_모델, index)         # 이미 올려 둔 모델을 쓴다


client = TestClient(app)
print(client.get("/fast/0").json())
for 주소 in ["/slow", "/fast"]:
    걸린_시간 = []
    for i in range(50):
        시작 = time.perf_counter()
        client.get(f"{주소}/{i}")
        걸린_시간.append((time.perf_counter() - 시작) * 1000)
    print(f"{주소:5}: 요청 하나에 {statistics.median(걸린_시간):.2f}ms (중앙값)")
```

```text
{'예측': '앵클부츠', '정답': '앵클부츠'}
/slow: 요청 하나에 3.73ms (중앙값)
/fast: 요청 하나에 1.85ms (중앙값)
```

0번 시험 사진을 앵클부츠로 맞혔으니 서버는 제대로 돕니다. 시간을 보면 요청마다 모델을 불러오는 `/slow`가 미리 올려 둔 `/fast`보다 두 배쯤 걸렸어요. 이 모델은 1.6MB짜리라 차이가 1~2ms에 그치지만, 모델이 커지면 이야기가 달라집니다. 이 책의 실행 환경에서 14장의 0.5B 언어 모델은 파일이 이미 메모리 캐시에 올라와 있는데도 불러오는 데만 0.2~0.4초가 걸렸어요. 계산은 시작도 안 했는데요. 게다가 요청 열 개가 동시에 들어오면 2GB짜리 모델이 메모리에 열 벌 올라갑니다.

이 비교로 원칙 하나를 얻습니다. **모델은 서버가 켜질 때 한 번 불러오고, 요청은 그 모델을 같이 쓴다.** 위 코드의 `/fast`는 모델을 모듈 맨 위의 전역 변수에 올려서 이 원칙을 지켰어요. 그런데 이 방법에는 문제가 있습니다. 다음 절에서 그 문제와 FastAPI가 준비한 정식 방법을 보겠습니다.

## 20.2 서버가 켜질 때 한 번만: lifespan

### 전역 변수로 올리면 무엇이 불편할까요?

모듈 맨 위에서 모델을 불러오면 `import`하는 순간 모델이 올라갑니다. 테스트 코드가 경로 함수 하나만 확인하려고 `import`해도 무거운 모델이 올라오고, 모델 파일이 없는 컴퓨터에서는 `import` 자체가 실패해요. 서버가 꺼질 때 GPU 메모리를 비우거나 연결을 닫는 정리 작업을 넣을 자리도 없습니다.

FastAPI는 이를 위해 **lifespan**(수명)이라는 자리를 마련해 두었습니다. 1권 15장의 `@asynccontextmanager`로 함수를 하나 만들면, `yield` 앞은 서버가 요청을 받기 **직전에**, `yield` 뒤는 서버가 꺼질 때 실행돼요. 식당으로 치면 문 열기 전 준비와 문 닫은 뒤 정리입니다.

```python
from contextlib import asynccontextmanager

import torch
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from 서빙도구 import 모델_불러오기, 클래스_이름


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[시작] 모델을 올립니다")
    app.state.모델 = 모델_불러오기()          # 서버가 시작될 때 딱 한 번
    yield                                      # 여기서 요청을 받는다
    print("[종료] 모델을 내립니다")
    del app.state.모델


app = FastAPI(lifespan=lifespan)


@app.get("/predict/blank")
def 빈_사진_예측(request: Request) -> dict:
    모델 = request.app.state.모델              # 시작할 때 올려 둔 모델 꺼내기
    with torch.no_grad():
        점수 = 모델(torch.zeros(1, 1, 28, 28))
    return {"예측": 클래스_이름[점수.argmax().item()]}


with TestClient(app) as client:              # with 블록에 들어갈 때 시작, 나올 때 종료
    print(client.get("/predict/blank").json())
    print(client.get("/predict/blank").json())
print("with 블록 밖")

client = TestClient(app)                     # with 없이 쓰면 lifespan이 돌지 않는다
try:
    client.get("/predict/blank")
except AttributeError as e:
    print("오류:", e)
```

```text
[시작] 모델을 올립니다
{'예측': '샌들'}
{'예측': '샌들'}
[종료] 모델을 내립니다
with 블록 밖
오류: 'State' object has no attribute '모델'
```

출력 순서를 보세요. `[시작]`이 요청보다 먼저, `[종료]`가 마지막 요청 뒤에 찍혔습니다. 요청이 두 번 왔지만 모델은 한 번만 올라갔어요.

- **`FastAPI(lifespan=lifespan)`**: 앱을 만들 때 수명 함수를 넘깁니다.
- **`app.state`**: 앱에 딸린 보관함입니다. 아무 이름이나 붙여 값을 넣어 둘 수 있어요. 시작할 때 넣은 모델을 경로 함수에서 `request.app.state.모델`로 꺼내 씁니다. 매개변수에 `request: Request`를 적으면 FastAPI가 지금 요청 객체를 넣어 줘요.
- **빈 사진의 예측**: 아무것도 없는 검은 사진을 넣었는데 모델은 "샌들"이라고 답했습니다. 분류 모델은 열 가지 중 하나를 반드시 고르게 만들어져서 "모르겠다"고 하지 못해요. 서빙할 때는 이 점을 기억해 두세요. 엉뚱한 사진에도 자신 있게 틀린 답을 냅니다.

마지막 부분이 이 절에서 가장 중요합니다. `TestClient`를 `with` 없이 만들어 요청하면 lifespan이 실행되지 않아서 `app.state`에 모델이 없다는 `AttributeError`가 나요. 1권 19장에서는 lifespan이 없었으니 `with` 없이 써도 괜찮았지만, 이제부터는 **`with TestClient(app) as client:`** 로 써야 서버가 시작·종료되는 과정까지 흉내 냅니다. 실제 서버인 uvicorn은 언제나 lifespan을 실행하니, 이 실수는 테스트에서만 나타나서 더 헷갈려요.

> **Q. 예전 코드에서 `@app.on_event("startup")`을 봤는데, 그건 뭔가요?**
> lifespan이 생기기 전에 쓰던 방법입니다. 시작할 때 할 일과 끝날 때 할 일을 서로 다른 함수 두 개에 나눠 적었는데, 그러면 시작할 때 만든 값을 끝날 때 함수로 넘기기 번거로웠어요. 지금 쓰면 "on_event는 더 이상 권하지 않으니 lifespan을 쓰라"는 경고(`DeprecationWarning`)가 나와요. 하나의 함수 안에서 `yield` 앞뒤로 준비와 정리가 짝을 이루니, 1권 12장의 `with` 문처럼 "열었으면 반드시 닫는다"가 눈에 보입니다.

## 20.3 주문서 양식: 요청과 응답 스키마

옷 분류기에 넣을 값은 28 × 28 크기에 0~1 사이 실수여야 합니다. 1권 19.5절에서 Pydantic으로 "주문서 양식"을 정해 두면 잘못된 주문서는 경로 함수에 닿기 전에 422로 돌려보낸다고 했죠. 모델 서빙에서는 이 검사가 더 중요해요. 모양이 틀린 입력이 모델에 들어가면 4장 4.10절의 모양 오류가 서버 안에서 터져 500이 되거나, 더 나쁘게는 오류 없이 엉뚱한 답이 나가거든요.

이번에는 사진을 숫자 목록(28줄 × 28칸)으로 받고, 응답도 Pydantic 모델로 정해 보겠습니다. 응답 모양을 정해 두면 자동 문서(1권 19.4절)에 "이런 모양이 돌아온다"가 적혀서, API를 쓰는 친구가 코드를 읽지 않아도 됩니다.

```python
from contextlib import asynccontextmanager
from typing import Annotated

import torch
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from torchvision import datasets
from torchvision.transforms.functional import to_tensor

from 서빙도구 import 모델_불러오기, 클래스_이름

픽셀 = Annotated[float, Field(ge=0.0, le=1.0)]                  # 칸 하나: 0~1 사이 실수
한_줄 = Annotated[list[픽셀], Field(min_length=28, max_length=28)]


class PixelInput(BaseModel):
    pixels: Annotated[list[한_줄], Field(min_length=28, max_length=28)]   # 28줄 × 28칸


class Prediction(BaseModel):
    label: str
    class_id: int
    probability: float


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.모델 = 모델_불러오기()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/predict")
def 예측(입력: PixelInput, request: Request) -> Prediction:
    x = torch.tensor(입력.pixels).reshape(1, 1, 28, 28)
    with torch.no_grad():
        확률 = request.app.state.모델(x).softmax(dim=1)[0]
    번호 = 확률.argmax().item()
    return Prediction(label=클래스_이름[번호], class_id=번호,
                      probability=round(확률[번호].item(), 4))


사진, 정답 = datasets.FashionMNIST("data", train=False, download=True)[0]
픽셀값 = to_tensor(사진)[0].tolist()                               # 28 × 28 리스트
with TestClient(app) as client:
    응답 = client.post("/predict", json={"pixels": 픽셀값})
    print(응답.status_code, 응답.json(), "정답:", 클래스_이름[정답])

    잘못된_입력 = {"pixels": 픽셀값[:27]}                             # 27줄뿐
    잘못된_입력["pixels"][3][5] = 2.0                                 # 1보다 큰 값
    for 차례 in range(2):
        응답 = client.post("/predict", json=잘못된_입력)
        print(응답.status_code, [(오류["loc"], 오류["msg"]) for 오류 in 응답.json()["detail"]])
        잘못된_입력["pixels"][3][5] = 0.5                             # 값을 고쳐서 다시 보내기
    print(sorted(client.get("/openapi.json").json()["components"]["schemas"]))
```

```text
200 {'label': '앵클부츠', 'class_id': 9, 'probability': 0.9973} 정답: 앵클부츠
422 [(['body', 'pixels', 3, 5], 'Input should be less than or equal to 1')]
422 [(['body', 'pixels'], 'List should have at least 28 items after validation, not 27')]
['HTTPValidationError', 'PixelInput', 'Prediction', 'ValidationError']
```

0번 시험 사진을 보냈더니 앵클부츠일 확률 0.9973이라는 답이 응답 모델 `Prediction`의 모양 그대로 왔습니다. 경로 함수가 `-> Prediction`으로 응답 모양을 밝혔으니(1권 19.6절), 마지막 줄처럼 자동 문서의 스키마 목록에도 `PixelInput`과 `Prediction`이 올라 있어요.

입력 양식은 `Annotated`로 층층이 쌓았습니다. 칸 하나는 0~1 사이 실수, 한 줄은 그런 칸이 정확히 28개, 사진은 그런 줄이 정확히 28개예요. JSON 필드 이름(`pixels`, `label`)과 모델 클래스 이름(`PixelInput`, `Prediction`)은 1권 19.5절 Q&A에서 본 이유로 영어로 지었습니다.

잘못된 요청 두 번의 결과는 조금 흥미롭습니다. 27줄짜리 사진에 3번 줄 5번 칸이 2.0인 요청을 보냈는데, 첫 응답은 **칸 값**만 지적하고 줄 수는 말하지 않았어요. 칸 값을 고쳐 다시 보내자 그제야 "28개 이상이어야 하는데 27개"라고 알려 줍니다. Pydantic은 목록 안의 값을 먼저 검사하고, 그게 통과해야 목록의 길이를 셉니다. 그러니 422 응답을 받고 한 곳만 고쳤는데 또 다른 오류가 나와도 당황하지 마세요. `loc`의 `['body', 'pixels', 3, 5]`처럼 오류 위치가 정확히 찍히니 하나씩 고치면 됩니다.

다만 이 방법은 사진 한 장을 숫자 784개짜리 JSON으로 보내야 해서, 앱에서 쓰기에 번거롭고 크기도 큽니다. 실제 앱은 사진 **파일**을 그대로 올리죠. 다음 절에서 파일을 받아 보겠습니다.

## 20.4 사진 파일 받기

### UploadFile로 받기

파일은 JSON 본문이 아니라 **multipart/form-data**라는 형식으로 옵니다. 웹 페이지의 "파일 선택" 버튼이 보내는 형식이에요. FastAPI에서는 매개변수 타입을 `UploadFile`로, 기본값을 `File(...)`로 적으면 됩니다. 받은 파일은 Pillow로 열어서 학습 데이터와 같은 **흑백 28 × 28**로 바꾸고, 9장처럼 `to_tensor`로 0~1 사이 실수 텐서를 만듭니다.

```python
import io
from contextlib import asynccontextmanager

import torch
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.testclient import TestClient
from PIL import Image, UnidentifiedImageError
from torchvision import datasets
from torchvision.transforms.functional import to_tensor

from 서빙도구 import 모델_불러오기, 클래스_이름

최대_바이트 = 1_000_000                       # 사진 한 장은 1MB까지만 받는다


def 사진_전처리(데이터: bytes) -> torch.Tensor:
    """올라온 사진 파일을 학습 때와 같은 (1, 1, 28, 28) 텐서로 바꾼다."""
    try:
        사진 = Image.open(io.BytesIO(데이터))
        사진 = 사진.convert("L").resize((28, 28))          # 흑백, 28 × 28
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="사진 파일이 아닙니다")
    return to_tensor(사진).unsqueeze(0)                    # 0~1 실수, 배치 차원 추가


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.모델 = 모델_불러오기()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/predict/image")
def 사진_예측(request: Request, file: UploadFile = File(...)) -> dict:
    데이터 = file.file.read(최대_바이트 + 1)           # 한도보다 1바이트만 더 읽어 본다
    if len(데이터) > 최대_바이트:
        raise HTTPException(status_code=413, detail="파일이 너무 큽니다")
    with torch.no_grad():
        확률 = request.app.state.모델(사진_전처리(데이터)).softmax(dim=1)[0]
    return {"파일": file.filename, "예측": 클래스_이름[확률.argmax().item()],
            "확률": round(확률.max().item(), 4)}


def png_바이트(사진: Image.Image) -> bytes:
    버퍼 = io.BytesIO()
    사진.save(버퍼, format="PNG")
    return 버퍼.getvalue()


시험셋 = datasets.FashionMNIST("data", train=False, download=True)
사진, 정답 = 시험셋[1]
큰_컬러 = 사진.convert("RGB").resize((280, 280))               # 열 배 크게, 컬러로 바꾼 사진
보낼_것들 = {
    "옷.png": png_바이트(사진),
    "큰_컬러.png": png_바이트(큰_컬러),
    "메모.txt": "사진이 아니에요".encode(),
    "큰_파일.png": bytes(2_000_000),
}
with TestClient(app) as client:
    print("정답:", 클래스_이름[정답])
    for 이름, 내용 in 보낼_것들.items():
        응답 = client.post("/predict/image", files={"file": (이름, 내용)})
        print(f"{이름:10} {len(내용):>9,}바이트 → {응답.status_code} {응답.json()}")
```

```text
정답: 풀오버
옷.png            594바이트 → 200 {'파일': '옷.png', '예측': '풀오버', '확률': 0.9998}
큰_컬러.png      21,698바이트 → 200 {'파일': '큰_컬러.png', '예측': '풀오버', '확률': 0.999}
메모.txt            22바이트 → 400 {'detail': '사진 파일이 아닙니다'}
큰_파일.png   2,000,000바이트 → 413 {'detail': '파일이 너무 큽니다'}
```

네 가지 파일을 보냈습니다.

- **옷.png**: 1번 시험 사진(풀오버)을 PNG로 저장한 594바이트짜리 파일입니다. 숫자 784개짜리 JSON보다 훨씬 작죠.
- **큰_컬러.png**: 같은 사진을 열 배 키우고 컬러로 바꿨는데도 `convert("L")`(흑백)과 `resize((28, 28))`를 거쳐 같은 답이 나왔어요.
- **메모.txt**: 사진이 아닌 파일은 Pillow가 `UnidentifiedImageError`를 냅니다. 이걸 잡아서 `400 Bad Request`로 바꿨어요. 잡지 않으면 FastAPI는 이를 서버 잘못으로 보고 500을 돌려줍니다. 손님이 잘못 보낸 것은 4xx, 서버가 잘못한 것은 5xx라는 1권 19.1절의 약속을 지키려면 예외를 알맞은 상태 코드로 바꿔 줘야 해요.
- **큰_파일.png**: 1MB가 넘는 파일은 `413`(내용이 너무 큼)으로 거절했습니다. 파일을 통째로 읽지 않고 **한도보다 1바이트만 더** 읽어 본 것이 요령이에요. 1바이트라도 더 읽혔다면 한도를 넘은 파일입니다. 이렇게 하면 누군가 10GB짜리 파일을 보내도 **메모리에 올리는 것**은 1MB 남짓뿐이에요. 다만 경로 함수가 실행될 때는 FastAPI(정확히는 그 밑의 Starlette)가 요청 본문을 이미 끝까지 받아서, 큰 파일은 임시 파일로 디스크에 써 둔 뒤입니다. 받는 것 자체를 막으려면 요청 머리의 `Content-Length`를 먼저 보고 거절하는 미들웨어(20.7절)를 두거나, 서버 앞에 둔 프록시에서 크기를 제한합니다(nginx라면 `client_max_body_size` 설정).

경로 함수를 `async def`가 아닌 그냥 `def`로 쓰고 파일을 `file.file.read()`로 읽은 데에는 이유가 있습니다. 20.6절에서 자세히 봐요.

### 학습 때와 같은 전처리

서빙에서 가장 흔하고 찾기 어려운 버그는 **학습할 때와 서빙할 때의 전처리가 다른 것**입니다. 10장 10.2절에서 사전학습 모델에 ImageNet의 평균과 표준편차를 맞춰 넣어야 했던 것과 같은 이야기예요. 오류는 나지 않고 정확도만 조용히 떨어지니 더 무섭습니다.

FashionMNIST는 **검은 배경에 밝은 옷**입니다. 그런데 쇼핑몰 상품 사진은 대개 흰 배경에 옷이 있죠. 이런 사진이 들어오면 어떻게 될까요? 시험 사진 1,000장으로 두 가지 실수를 흉내 내 보겠습니다. 이번에는 텐서 대신 NumPy 배열로 전처리하는데, 이유는 20.8절에서 밝혀집니다.

```python
import numpy as np
import torch
from PIL import Image, ImageOps
from torchvision import datasets

from 서빙도구 import 모델_불러오기

모델 = 모델_불러오기()
시험셋 = datasets.FashionMNIST("data", train=False, download=True)
사진들 = [시험셋[i][0] for i in range(1000)]
정답 = torch.tensor([시험셋[i][1] for i in range(1000)])


def 정확도(전처리, 사진_목록: list[Image.Image]) -> float:
    x = torch.stack([전처리(사진) for 사진 in 사진_목록])
    with torch.no_grad():
        return (모델(x).argmax(dim=1) == 정답).float().mean().item()


def 학습때와_같이(사진: Image.Image) -> torch.Tensor:
    배열 = np.asarray(사진.convert("L").resize((28, 28)), dtype=np.float32) / 255
    return torch.from_numpy(배열).unsqueeze(0)


def 나누기_빠뜨림(사진: Image.Image) -> torch.Tensor:
    배열 = np.asarray(사진.convert("L").resize((28, 28)), dtype=np.float32)   # 0~255 그대로
    return torch.from_numpy(배열).unsqueeze(0)


def 배경_맞추기(사진: Image.Image) -> torch.Tensor:
    x = 학습때와_같이(사진)
    테두리 = torch.cat([x[0, 0], x[0, -1], x[0, :, 0], x[0, :, -1]])
    return 1 - x if 테두리.mean() > 0.5 else x      # 배경이 밝으면 뒤집어 검은 배경으로


흰_배경 = [ImageOps.invert(사진) for 사진 in 사진들]   # 쇼핑몰 사진처럼 흰 배경에 어두운 옷
print(f"학습 때와 같은 전처리         : {정확도(학습때와_같이, 사진들):.1%}")
print(f"255로 나누기를 빠뜨림         : {정확도(나누기_빠뜨림, 사진들):.1%}")
print(f"흰 배경 사진, 그대로          : {정확도(학습때와_같이, 흰_배경):.1%}")
print(f"흰 배경 사진, 배경 맞추기     : {정확도(배경_맞추기, 흰_배경):.1%}")
print(f"원래 사진에 배경 맞추기를 써도: {정확도(배경_맞추기, 사진들):.1%}")
```

```text
학습 때와 같은 전처리         : 90.7%
255로 나누기를 빠뜨림         : 84.5%
흰 배경 사진, 그대로          : 28.4%
흰 배경 사진, 배경 맞추기     : 90.7%
원래 사진에 배경 맞추기를 써도: 90.7%
```

학습 때와 같은 전처리로는 1,000장 중 90.7%를 맞힙니다. 첫 번째 실수인 **255로 나누기를 빠뜨리면** 84.5%로 떨어졌어요. 값이 255배나 커졌는데 생각보다 덜 떨어졌죠? 그래서 더 위험합니다. 오류 없이 6%p를 잃었으니, 정확도를 따로 재 보지 않으면 알아챌 길이 없어요.

진짜 문제는 **흰 배경 사진**입니다. 흑백을 뒤집은 사진을 그대로 넣었더니 28.4%, 열 가지 중 아무거나 찍는 10%보다 조금 나은 수준까지 무너졌어요. 모델은 9장에서 배운 "밝은 부분의 모양"을 보는데, 배경 전체가 밝아졌으니 엉뚱한 것을 보게 된 거죠.

`배경_맞추기`는 사진 테두리의 평균 밝기를 보고, 0.5보다 밝으면 배경이 흰 사진으로 보고 뒤집습니다. 이 한 단계로 흰 배경 사진의 정확도가 원래와 같은 90.7%로 돌아왔어요. 그리고 마지막 줄처럼 원래 사진에 써도 정확도가 그대로입니다. FashionMNIST 사진은 테두리가 모두 어둡기 때문이에요. 이렇게 "학습 데이터처럼 생기지 않은 입력을 학습 데이터처럼 바꾸는" 단계는, 서빙할 곳의 실제 입력을 보고 나서야 알 수 있습니다. 그래서 서비스를 열고 나서도 어떤 사진이 들어오는지 꾸준히 들여다봐야 해요.

> **Q. 전처리 코드를 학습 코드와 서빙 코드에 따로 두면 안 되나요?**
> 따로 두면 언젠가는 어긋납니다. 학습 쪽에서 크기를 32 × 32로 바꿨는데 서빙 쪽은 28 × 28 그대로 둔다든지요. 가장 좋은 방법은 전처리 함수를 **한 곳에** 두고 학습과 서빙이 같이 `import`하는 것입니다. 그럴 수 없다면 이 절처럼 "같은 사진을 두 전처리에 넣으면 같은 결과가 나오는가"를 확인하는 테스트를 20.11절처럼 만들어 두세요. 10장 10.2절의 `weights.transforms()`처럼 모델과 전처리를 한 묶음으로 배포하는 것도 같은 생각입니다.

## 20.5 여러 장을 한 번에: 배치 추론

### 한 장씩 vs 묶어서

4장 4.2절에서 모델은 사진을 한 장씩이 아니라 **배치**로 묶어 처리한다고 했습니다. 그래야 계산 장치가 쉬지 않으니까요. 서빙에서는 이게 얼마나 차이를 낼까요? 사진 512장을 배치 크기를 바꿔 가며 처리하고 한 장당 시간을 재 보겠습니다. 4장 4.8절처럼 준비 운동을 한 뒤 일곱 번 재서 중앙값을 썼어요.

```python
import statistics
import time

import torch

from 서빙도구 import 모델_불러오기

torch.manual_seed(0)
모델 = 모델_불러오기()
사진들 = torch.rand(512, 1, 28, 28)                      # 시간만 잴 것이라 아무 사진이나


def 시간_재기(배치_크기: int, 반복: int = 7) -> float:
    """사진 512장을 배치_크기씩 나눠 처리할 때, 사진 한 장당 걸린 시간(ms)의 중앙값."""
    기록 = []
    with torch.no_grad():
        모델(사진들[:배치_크기])                           # 준비 운동 (4장 4.8절)
        for _ in range(반복):
            시작 = time.perf_counter()
            for i in range(0, len(사진들), 배치_크기):
                모델(사진들[i:i + 배치_크기])
            기록.append((time.perf_counter() - 시작) * 1000 / len(사진들))
    return statistics.median(기록)


print("배치 크기  한 장당 시간  한 장씩 대비")
기준 = 시간_재기(1)
for 크기 in [1, 8, 32, 128, 512]:
    걸림 = 기준 if 크기 == 1 else 시간_재기(크기)
    print(f"{크기:>7}  {걸림:9.3f}ms  {기준 / 걸림:8.1f}배")
```

```text
배치 크기  한 장당 시간  한 장씩 대비
      1      0.273ms       1.0배
      8      0.095ms       2.9배
     32      0.079ms       3.5배
    128      0.036ms       7.6배
    512      0.028ms       9.9배
```

이 책의 실행 환경(Apple M4 Max, CPU)에서 잰 값입니다. 한 장씩 넣으면 한 장에 0.27ms쯤 걸리던 것이, 128장씩 묶으면 0.04ms 아래로, 512장을 한꺼번에 넣으면 0.03ms 아래로 줄었어요. 같은 일을 열 배 가까이 빨리 한 셈입니다. 모델을 한 번 부를 때마다 드는 고정 비용(파이썬 함수 호출, 층마다 계산을 준비하는 일)을 여러 장이 나눠 내고, 큰 행렬 곱은 CPU의 여러 코어와 벡터 연산을 더 잘 활용하기 때문이에요. GPU라면 차이가 훨씬 더 큽니다(16장).

### 따로 온 요청을 모아서 한 번에

그렇다면 손님이 사진 여러 장을 한 번에 보내게 하면 되겠죠? 매개변수를 `list[UploadFile]`로 받으면 같은 이름으로 온 파일들이 목록이 됩니다. 20.11절 실습의 `/predict/batch`가 그렇게 만든 것인데, 한 요청이 너무 많은 장수를 보내면 그 계산이 끝날 때까지 다른 손님이 기다려야 하니 장수에 상한(32장)을 두었어요. 그런데 실제 손님은 대개 사진을 **한 장씩, 따로따로** 보냅니다. 앱 사용자 64명이 동시에 사진을 하나씩 올리는 식이죠. 손님 쪽을 바꿀 수 없다면 서버 쪽에서 모으면 됩니다. 버스 정류장을 떠올려 보세요. 버스는 손님 한 명이 올 때마다 출발하지 않고, 자리가 차거나 정해진 시간이 되면 출발합니다. 서버도 첫 요청이 오면 아주 잠깐(여기서는 5ms) 더 기다리면서 다른 요청을 모았다가, 32장이 차거나 시간이 다 되면 모델을 한 번 부르는 거예요. 이런 방법을 **동적 배칭(dynamic batching)** 이라고 합니다.

asyncio의 `Queue`(대기 줄)와, 1권 15장에서 어웨이터블의 하나로 이름만 봤던 `Future`(나중에 답이 채워질 빈자리)로 만들 수 있습니다. 동시에 64명이 요청하는 상황은 `TestClient`로 만들기 어려워서, `TestClient`가 안에서 쓰는 `httpx2`의 비동기 클라이언트를 직접 썼어요. `ASGITransport`는 네트워크를 거치지 않고 앱에 바로 요청을 넣는 연결입니다.

```python
import asyncio
import io
from contextlib import asynccontextmanager

import httpx2
import numpy as np
import torch
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from PIL import Image

from 서빙도구 import 모델_불러오기, 시험_사진_파일, 클래스_이름


class 배치_모으기:
    """따로 온 요청을 잠깐 모았다가 모델을 한 번만 부른다."""

    def __init__(self, 모델: torch.nn.Module, 최대_장수: int = 32,
                 최대_대기: float = 0.005) -> None:
        self.모델, self.최대_장수, self.최대_대기 = 모델, 최대_장수, 최대_대기
        self.큐: asyncio.Queue = asyncio.Queue()
        self.배치_기록: list[int] = []

    async def 예측(self, x: np.ndarray) -> int:
        결과_자리 = asyncio.get_running_loop().create_future()   # 나중에 답이 들어올 빈자리
        await self.큐.put((x, 결과_자리))
        return await 결과_자리                                   # 답이 채워질 때까지 기다린다

    async def 계속_돌리기(self) -> None:
        루프 = asyncio.get_running_loop()
        while True:
            묶음 = [await self.큐.get()]                         # 첫 요청이 올 때까지 기다리고
            마감 = 루프.time() + self.최대_대기                   # 그때부터 잠깐만 더 모은다
            while len(묶음) < self.최대_장수 and (남은 := 마감 - 루프.time()) > 0:
                try:
                    묶음.append(await asyncio.wait_for(self.큐.get(), 남은))
                except TimeoutError:
                    break
            x = torch.from_numpy(np.stack([x for x, _ in 묶음]))
            번호들 = await run_in_threadpool(self.계산, x)       # 계산은 스레드에서 (20.6절)
            for (_, 결과_자리), 번호 in zip(묶음, 번호들):
                결과_자리.set_result(번호)
            self.배치_기록.append(len(묶음))

    def 계산(self, x: torch.Tensor) -> list[int]:
        with torch.no_grad():
            return self.모델(x).argmax(dim=1).tolist()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.모으기 = 배치_모으기(모델_불러오기())
    일꾼 = asyncio.create_task(app.state.모으기.계속_돌리기())   # 뒤에서 계속 도는 작업
    yield
    일꾼.cancel()


app = FastAPI(lifespan=lifespan)


@app.post("/predict/image")
async def 사진_예측(request: Request, file: UploadFile = File(...)) -> dict:
    # 28 × 28짜리 작은 사진이라 이벤트 루프에서 바로 전처리했다. 무거운 전처리라면 20.6절처럼 스레드로 넘긴다
    사진 = Image.open(io.BytesIO(await file.read())).convert("L").resize((28, 28))
    x = np.asarray(사진, dtype=np.float32)[None] / 255
    return {"label": 클래스_이름[await request.app.state.모으기.예측(x)]}


async def 손님_64명() -> None:
    파일들 = 시험_사진_파일(64)
    async with lifespan(app):                                   # TestClient 대신 직접 시작·종료
        전송 = httpx2.ASGITransport(app=app)
        async with httpx2.AsyncClient(transport=전송, base_url="http://test") as client:
            요청들 = [client.post("/predict/image", files={"file": ("x.png", 내용)})
                      for 내용, _ in 파일들]
            응답들 = await asyncio.gather(*요청들)
        맞힘 = sum(r.json()["label"] == 클래스_이름[답] for r, (_, 답) in zip(응답들, 파일들))
        기록 = app.state.모으기.배치_기록
        print(f"요청 {len(응답들)}개 → 모델 호출 {len(기록)}번, 배치 크기 {기록}")
        print(f"64장 중 {맞힘}장 정답")


asyncio.run(손님_64명())
```

```text
요청 64개 → 모델 호출 2번, 배치 크기 [32, 32]
64장 중 58장 정답
```

요청 64개가 들어왔는데 모델은 **두 번**만 불렸고, 한 번에 32장씩 처리했습니다. 64장 중 58장(90.6%)을 맞혀 정확도도 그대로예요. 흐름을 따라가 보겠습니다.

1. 경로 함수 `사진_예측`은 사진을 전처리한 뒤 `모으기.예측(x)`를 `await`합니다. `예측`은 빈자리(`Future`)를 하나 만들어 사진과 함께 대기 줄에 넣고, 그 자리에 답이 채워질 때까지 기다려요. 기다리는 동안 이벤트 루프는 다른 요청을 받습니다.
2. lifespan에서 `asyncio.create_task`로 띄워 둔 `계속_돌리기`가 뒤에서 계속 돕니다. 대기 줄에서 첫 사진을 꺼내면 마감 시각을 정하고, 마감 전까지 최대 32장을 더 꺼내 모아요.
3. 모은 사진을 `np.stack`으로 한 배치로 쌓아 모델을 한 번 부르고, 답을 각자의 빈자리에 `set_result`로 채웁니다. 그러면 1번에서 기다리던 경로 함수들이 깨어나 응답을 돌려줘요.

최대 대기 시간은 손님이 손해를 보는 시간입니다. 요청이 드물 때는 첫 손님이 5ms를 그냥 기다리니까요. 대신 요청이 몰리면 모델 호출이 수십 분의 1로 줄어 처리량이 오릅니다. 작은 모델에서는 이득이 크지 않지만, 한 번 부르는 비용이 큰 GPU 모델에서는 서빙 도구들이 기본으로 갖추는 기능이에요.

## 20.6 오래 걸리는 계산과 async

### 이벤트 루프를 막으면

1권 19.2절에서 `async def` 경로 함수는 이벤트 루프에서 직접 실행되고, 그냥 `def`는 FastAPI가 따로 마련한 작업 스레드에서 실행된다고 했습니다. 그리고 1권 15장에서 `async def` 안에서 `time.sleep()`처럼 멈추는 코드를 부르면 이벤트 루프 전체가 멈춘다고 했죠. 모델 추론도 그런 코드입니다. `await`할 곳 없이 CPU로 계산만 하니까요.

직접 확인해 보겠습니다. 요청 하나에 사진 3,000장을 계산하는 무거운 예측 API를 세 가지 방식으로 만들고, 예측 요청 네 개를 보낸 직후에 가벼운 `/health` 요청을 하나 보냅니다. `/health`의 답이 언제 오는지가 관심사예요.

```python
import asyncio
import time

import httpx2
import torch
from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool

from 서빙도구 import 모델_불러오기

모델 = 모델_불러오기()
사진들 = torch.rand(3000, 1, 28, 28)       # 요청 하나에 계산이 꽤 걸리게 3,000장


def 무거운_추론() -> int:
    with torch.no_grad():
        return 모델(사진들).argmax(dim=1)[0].item()


def 앱_만들기(방식: str) -> FastAPI:
    app = FastAPI()

    if 방식 == "async def에서 바로":
        @app.get("/predict")
        async def 예측() -> dict:
            return {"label": 무거운_추론()}           # 이벤트 루프 위에서 계산
    elif 방식 == "그냥 def":
        @app.get("/predict")
        def 예측() -> dict:
            return {"label": 무거운_추론()}           # FastAPI가 스레드에서 실행
    else:
        @app.get("/predict")
        async def 예측() -> dict:
            return {"label": await run_in_threadpool(무거운_추론)}   # 계산만 스레드로

    @app.get("/health")
    async def 상태() -> dict:
        return {"status": "ok"}

    return app


async def 시험하기(방식: str) -> None:
    전송 = httpx2.ASGITransport(app=앱_만들기(방식))
    async with httpx2.AsyncClient(transport=전송, base_url="http://test") as client:
        async def 상태_확인() -> float:
            await asyncio.sleep(0.01)                  # 예측 요청들이 먼저 시작하게
            await client.get("/health")
            return time.perf_counter() - 시작          # 처음부터 /health 답을 받기까지

        시작 = time.perf_counter()
        예측들 = [client.get("/predict") for _ in range(4)]
        *_, 상태_시각 = await asyncio.gather(*예측들, 상태_확인())
        끝 = time.perf_counter() - 시작
        print(f"{방식:18}: 예측 4개 끝 {끝:.2f}초, /health 답 {상태_시각:.2f}초")


무거운_추론()                                        # 준비 운동
for 방식 in ["async def에서 바로", "그냥 def", "run_in_threadpool"]:
    asyncio.run(시험하기(방식))
```

```text
async def에서 바로    : 예측 4개 끝 0.37초, /health 답 0.37초
그냥 def            : 예측 4개 끝 0.34초, /health 답 0.02초
run_in_threadpool : 예측 4개 끝 0.35초, /health 답 0.03초
```

- **async def에서 바로**: `/health`의 답이 예측 네 개가 모두 끝난 뒤에야 왔습니다. 계산하는 동안 이벤트 루프가 멈춰서, "살아 있니?"라는 한 마디에도 대답하지 못한 거예요. 실제 서비스라면 감시 프로그램이 이 서버를 "죽었다"고 판단해 재시작해 버릴 수도 있습니다.
- **그냥 def**: FastAPI가 경로 함수를 작업 스레드에서 돌리니, 이벤트 루프는 자유롭게 `/health`에 바로 답했어요.
- **run_in_threadpool**: `async def` 안에서 다른 비동기 작업(`await`)을 써야 하는데 무거운 계산도 해야 할 때는, 계산 부분만 `await run_in_threadpool(함수)`로 작업 스레드에 넘깁니다. 1권 15장의 `asyncio.to_thread`와 같은 일을 FastAPI가 쓰는 스레드 묶음에서 해 주는 함수예요. 20.5절의 동적 배칭도 이 방법으로 모델을 불렀습니다.

규칙으로 정리하면 이렇습니다. **모델 추론을 하는 경로 함수는 그냥 `def`로 쓴다. `async def`가 꼭 필요하면 추론만 `run_in_threadpool`로 넘긴다.** 20.4절에서 파일을 `await file.read()` 대신 `file.file.read()`로 읽고 `def`로 쓴 것도 이 때문이었어요.

한 가지 더 보세요. 세 방식 모두 예측 네 개가 끝나는 데는 비슷하게 0.3초 남짓 걸렸습니다. 스레드로 넘겼다고 계산이 빨라지지는 않아요. PyTorch는 큰 계산 하나에 이미 CPU 코어를 여럿 쓰고 있어서, 스레드를 늘려도 코어를 나눠 쓸 뿐입니다. 스레드의 역할은 계산을 빠르게 하는 것이 아니라 **계산하는 동안에도 서버가 다른 손님에게 대답할 수 있게** 하는 거예요.

> **Q. PyTorch는 GIL 때문에 스레드에서 느려지지 않나요?**
> 1권 15장에서 파이썬 코드는 GIL 때문에 한 번에 한 스레드만 실행된다고 했죠. 그런데 PyTorch와 ONNX Runtime의 무거운 계산은 C++ 코드 안에서 일어나고, 그동안은 GIL을 내려놓습니다. 그래서 한 스레드가 계산하는 동안 다른 스레드가 요청을 해석하고 응답을 만들 수 있어요. 위 실험에서 `/health`가 바로 답한 것이 그 증거입니다.

## 20.7 살아 있나, 준비됐나, 무슨 모델인가

### 헬스 체크와 버전 정보

띄워 둔 서버가 잘 도는지는 대개 Docker나 클라우드의 감시 프로그램이 몇 초마다 물어서 확인합니다. 그래서 서빙 서버에는 이런 주소를 둬요.

- **`/health`**: "살아 있니?" 프로세스가 응답할 수 있으면 200. 응답이 없으면 감시 프로그램이 서버를 재시작합니다.
- **`/ready`**: "손님 받을 준비 됐니?" 모델까지 올라와야 200, 아니면 `503 Service Unavailable`. 준비가 안 된 서버에는 요청을 보내지 않습니다.
- **`/version`**: "지금 무슨 모델로 답하고 있니?" 앱 버전, 모델 파일과 그 **지문**(해시), 라이브러리 버전을 알려 줍니다.

마지막이 의외로 중요합니다. "어제부터 답이 이상하다"는 연락을 받았을 때, 지금 서버에 올라간 모델이 정확히 어떤 파일인지 모르면 원인을 찾을 수가 없어요. 18장에서 데이터와 모델 파일을 해시로 기록한 것처럼, 서버도 자기가 올린 모델 파일의 sha256 해시를 알려 주게 하겠습니다. 덤으로 모든 응답 헤더에 처리 시간과 모델 지문을 붙이는 **미들웨어**도 달아요. 미들웨어는 모든 요청이 경로 함수에 가기 전과 후에 거치는 관문입니다.

```python
import hashlib
import time
from contextlib import asynccontextmanager
from pathlib import Path

import torch
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient

from 서빙도구 import 모델_불러오기

앱_버전 = "1.0.0"
모델_경로 = Path("fashion_cnn.pt")


def 파일_지문(경로: Path) -> str:
    """파일 내용의 sha256 해시 앞 12글자: 내용이 한 바이트만 달라도 바뀐다."""
    return hashlib.sha256(경로.read_bytes()).hexdigest()[:12]


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.모델 = 모델_불러오기(모델_경로)
    app.state.모델_지문 = 파일_지문(모델_경로)
    yield


app = FastAPI(lifespan=lifespan, version=앱_버전)


@app.middleware("http")
async def 처리_시간_기록(request: Request, call_next):
    시작 = time.perf_counter()
    응답 = await call_next(request)                       # 실제 경로 함수 실행
    응답.headers["X-Process-Time-ms"] = f"{(time.perf_counter() - 시작) * 1000:.2f}"
    응답.headers["X-Model-Version"] = getattr(request.app.state, "모델_지문", "none")
    return 응답


@app.get("/health")
def 살아있나() -> dict:
    return {"status": "ok"}                               # 프로세스가 응답할 수 있는가


@app.get("/ready")
def 준비됐나(request: Request, response: Response) -> dict:
    if not hasattr(request.app.state, "모델"):            # 모델이 올라왔는가
        response.status_code = 503
        return {"ready": False}
    return {"ready": True}


@app.get("/version")
def 버전(request: Request) -> dict:
    return {"app": 앱_버전, "model_file": 모델_경로.name,
            "model_sha256": request.app.state.모델_지문, "torch": torch.__version__}


아직 = TestClient(app)                                   # lifespan 전: 모델이 아직 없다
print("시작 전:", 아직.get("/health").json(), 아직.get("/ready").status_code)
with TestClient(app) as client:
    print("시작 후:", client.get("/health").json(), client.get("/ready").status_code)
    응답 = client.get("/version")
    print(응답.json())
    print({k: v for k, v in 응답.headers.items() if k.startswith("x-")})
```

```text
시작 전: {'status': 'ok'} 503
시작 후: {'status': 'ok'} 200
{'app': '1.0.0', 'model_file': 'fashion_cnn.pt', 'model_sha256': 'fa2fe8ec0e5a', 'torch': '2.14.1'}
{'x-process-time-ms': '0.58', 'x-model-version': 'fa2fe8ec0e5a'}
```

- **시작 전**: 20.2절의 함정을 일부러 다시 썼습니다. lifespan이 돌기 전에는 `/health`는 200이지만 `/ready`는 503이에요. 프로세스는 살아 있지만 모델이 아직 없다는 뜻입니다. 큰 모델을 불러오는 데 몇십 초씩 걸리는 서버라면 이 구분이 꼭 필요해요.
- **시작 후**: 둘 다 200입니다.
- **`/version`**: 모델 파일의 sha256 앞 12글자 `fa2fe8ec0e5a`가 찍혔습니다. 파일 내용이 한 바이트만 달라도 이 값이 완전히 바뀌니, 두 서버가 같은 모델을 쓰는지 이 값만 비교하면 됩니다. 9장을 다른 환경에서 학습했다면 여러분의 값은 다를 거예요.
- **헤더**: `@app.middleware("http")`로 만든 `처리_시간_기록`이 `call_next(request)`로 경로 함수를 실행하기 전후의 시간을 재서 `X-Process-Time-ms` 헤더에 적고, `X-Model-Version`도 붙였습니다. 본문을 바꾸지 않고도 모든 응답에 정보를 실을 수 있어요. 이름 앞의 `X-`는 표준이 아닌, 우리가 정한 헤더라는 관례입니다.

## 20.8 ONNX Runtime으로 백엔드 바꾸기

### 서버 안에서 PyTorch 빼기

19장에서 ONNX 파일로 내보낸 모델은 PyTorch 없이 ONNX Runtime만으로 같은 답을 냈습니다. 서버에 쓰면 좋은 점이 셋이에요. 같은 CPU에서 더 빠르고(19장), 설치할 것이 훨씬 작고(20.11절의 Docker 이미지), pickle이 아니라서 열 때 코드가 실행될 걱정이 없습니다.

내보내는 방법은 19장 19.2절과 19.4절 그대로입니다. 서빙에 맞게 두 가지만 정했어요. 묶음 크기(`batch`)를 열어 둬서 20.5절의 배치 추론이 되게 하되 `min=1, max=1024`로 범위를 적어 두었고(서버가 받는 장수 상한보다 넉넉하게 잡은 값입니다), 입출력 이름은 다른 언어로 짠 프로그램도 이 파일을 그대로 열 수 있게 19장의 `사진`·`점수` 대신 영어 `image`와 `logits`로 붙였습니다.

```python
from pathlib import Path

import numpy as np
import onnxruntime as ort
import torch

from 서빙도구 import 모델_불러오기

모델 = 모델_불러오기("fashion_cnn.pt")
배치 = torch.export.Dim("batch", min=1, max=1024)          # 첫 차원(장 수)은 바뀔 수 있다
torch.onnx.export(모델, (torch.zeros(1, 1, 28, 28),), "fashion_cnn.onnx", dynamo=True,
                  input_names=["image"], output_names=["logits"],
                  dynamic_shapes={"x": {0: 배치}},
                  external_data=False, verbose=False)   # 가중치까지 한 파일에, 진행 메시지 끄기
for 파일 in sorted(Path(".").glob("fashion_cnn.*")):
    print(f"{파일.name:17} {파일.stat().st_size / 1024:7.1f} KB")

세션 = ort.InferenceSession("fashion_cnn.onnx", providers=["CPUExecutionProvider"])
print("입력:", [(i.name, i.shape) for i in 세션.get_inputs()])
print("출력:", [(o.name, o.shape) for o in 세션.get_outputs()])

torch.manual_seed(0)
for 장수 in [1, 64]:
    x = torch.rand(장수, 1, 28, 28)
    with torch.no_grad():
        파이토치 = 모델(x).numpy()
    런타임 = 세션.run(["logits"], {"image": x.numpy()})[0]
    같은_답 = (파이토치.argmax(1) == 런타임.argmax(1)).all()
    print(f"{장수:2}장: 최대 오차 {np.abs(파이토치 - 런타임).max():.2e}, 예측 모두 같음 {같은_답}")
```

```text
fashion_cnn.onnx   1662.5 KB
fashion_cnn.pt     1650.8 KB
입력: [('image', ['batch', 1, 28, 28])]
출력: [('logits', ['batch', 10])]
 1장: 최대 오차 5.13e-06, 예측 모두 같음 True
64장: 최대 오차 4.53e-06, 예측 모두 같음 True
```

`external_data=False`로 가중치까지 파일 하나에 담았더니 `.pt`와 거의 같은 1.6MB입니다. 입력과 출력의 첫 차원이 `batch`라는 이름으로 열려 있고, 1장과 64장 모두 PyTorch와의 차이가 100만분의 5 정도라서 예측은 하나도 다르지 않아요. 이 정도 차이가 왜 생기는지는 19장 19.3절에서 설명했습니다.

### 같은 약속, 다른 구현

이제 서버가 PyTorch 모델과 ONNX 모델 중 무엇이든 쓸 수 있게 하고 싶습니다. 핵심은 경로 함수가 "어떤 엔진으로 계산하는지"를 몰라도 되게 하는 거예요. 그러려면 두 엔진 사이에 **약속**을 하나 정합니다. "(N, 1, 28, 28) NumPy 배열을 받아 (N, 10) 점수 배열을 돌려주는 `점수` 메서드가 있다." 경로 함수는 이 약속만 믿고 부르고, 어느 엔진을 쓸지는 코드가 아니라 환경 변수로 정해요. 1권 19.7절에서 비밀 값을 코드 밖에 둔 것과 같은 생각입니다. 이 설계는 20.11절 실습의 `backends.py`에서 코드로 만나요.

여기서 짚어 둘 것은 약속의 재료가 텐서가 아니라 **NumPy 배열**이라는 점입니다. 20.4절에서 전처리를 NumPy로 바꿔 둔 이유가 이거예요. 전처리나 약속에 torch가 끼어 있으면, ONNX 엔진을 고르더라도 서버에 PyTorch를 깔아야 하거든요.

속도는 19장 19.7절에서 잰 것처럼 이 CNN에서 ONNX Runtime이 PyTorch보다 두 배쯤 빨랐습니다. 그런데 20.7절의 처리 시간 헤더를 다시 보면 요청 하나가 0.58ms였어요. 모델 계산이 두 배 빨라지면 서버도 두 배 빨라질까요? 다음 절에서 재 봅니다.

## 20.9 지연 시간 재기: 평균에 속지 않기

서빙의 성적표는 정확도만이 아닙니다. 손님이 느끼는 것은 **지연 시간(latency)**, 즉 요청을 보내고 답을 받기까지 걸린 시간이에요. 그런데 지연 시간을 평균 하나로 보고하면 위험합니다. 100명 중 99명은 1ms 만에 답을 받고 한 명은 1초를 기다렸다면, 평균은 11ms쯤으로 괜찮아 보이지만 그 한 명은 앱이 멈췄다고 느낄 테니까요.

그래서 서빙에서는 **백분위수**로 봅니다. p50(중앙값)은 "절반의 요청이 이보다 빨랐다", p95는 "95%가 이보다 빨랐다", p99는 "99%가 이보다 빨랐다"는 뜻이에요. p99가 느린 서비스는 하루 100만 번 요청을 받으면 그중 1만 번을 오래 기다리게 합니다. 사진 500장을 차례로 보내 보겠습니다. 서버 안에서 전처리와 모델 계산에 걸린 시간은 **`Server-Timing`** 이라는 표준 헤더에 담아 돌려받았어요. 브라우저 개발자 도구도 이 헤더를 읽어 그래프로 보여 줍니다.

```python
import io
import statistics
import time
from contextlib import asynccontextmanager

import numpy as np
import onnxruntime as ort
from fastapi import FastAPI, File, Request, Response, UploadFile
from fastapi.testclient import TestClient
from PIL import Image

from 서빙도구 import 시험_사진_파일


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.세션 = ort.InferenceSession("fashion_cnn.onnx", providers=["CPUExecutionProvider"])
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/predict/image")
def 사진_예측(request: Request, response: Response, file: UploadFile = File(...)) -> dict:
    t0 = time.perf_counter()
    사진 = Image.open(io.BytesIO(file.file.read())).convert("L").resize((28, 28))
    x = np.asarray(사진, dtype=np.float32)[None, None] / 255
    t1 = time.perf_counter()
    점수 = request.app.state.세션.run(["logits"], {"image": x})[0]
    t2 = time.perf_counter()
    # 서버 안에서 단계별로 걸린 시간을 표준 헤더(Server-Timing)로 알려 준다
    전처리_ms, 모델_ms = (t1 - t0) * 1000, (t2 - t1) * 1000
    response.headers["Server-Timing"] = f"pre;dur={전처리_ms:.3f}, model;dur={모델_ms:.3f}"
    return {"class_id": int(점수.argmax())}


전체, 전처리, 모델 = [], [], []
with TestClient(app) as client:
    for 내용, _ in 시험_사진_파일(500):
        시작 = time.perf_counter()
        응답 = client.post("/predict/image", files={"file": ("x.png", 내용)})
        전체.append((time.perf_counter() - 시작) * 1000)
        단계 = dict(p.split(";dur=") for p in 응답.headers["server-timing"].split(", "))
        전처리.append(float(단계["pre"]))
        모델.append(float(단계["model"]))

print(f"첫 요청: {전체[0]:.2f}ms")
나머지 = 전체[1:]
백분위 = statistics.quantiles(나머지, n=100)                  # 1~99번째 백분위수
print(f"나머지 {len(나머지)}개: 평균 {statistics.mean(나머지):.2f}ms, p50 {백분위[49]:.2f}ms, "
      f"p95 {백분위[94]:.2f}ms, p99 {백분위[98]:.2f}ms, 최대 {max(나머지):.2f}ms")
print(f"그중 서버 안 (중앙값): 전처리 {statistics.median(전처리):.3f}ms, "
      f"모델 {statistics.median(모델):.3f}ms")
```

```text
첫 요청: 3.79ms
나머지 499개: 평균 1.23ms, p50 1.13ms, p95 1.85ms, p99 2.15ms, 최대 2.60ms
그중 서버 안 (중앙값): 전처리 0.053ms, 모델 0.073ms
```

이 책의 실행 환경에서 잰 값이라 실행할 때마다 조금씩 다르지만, 모양은 늘 비슷합니다.

- **첫 요청이 가장 느립니다.** 처음 쓰는 코드 경로를 불러오고, 메모리를 준비하는 일이 첫 요청에 몰려요. 서버를 띄운 직후 첫 손님이 느린 답을 받지 않게, lifespan에서 가짜 입력으로 모델을 한 번 돌려 두는 **준비 운동**(4장 4.8절)을 하기도 합니다.
- **평균은 중앙값보다 큽니다.** 가끔 느린 요청이 평균을 끌어올리기 때문이에요. p99와 최대값은 중앙값의 두 배쯤까지 벌어졌어요. 그 사이 운영체제가 다른 일을 했거나, 파이썬이 메모리를 정리했거나 하는 이유로 생기는 꼬리예요.
- **모델은 아주 작은 부분입니다.** 서버 안에서 전처리와 모델 계산을 합쳐도 0.13ms쯤인데, 요청 하나 전체는 1ms가 넘었어요. 나머지는 HTTP 요청을 만들고 해석하고, multipart 본문에서 파일을 꺼내고, 응답을 JSON으로 만드는 데 쓰였습니다. 이렇게 작은 모델에서는 모델을 더 빠르게 만들기보다 **요청 횟수를 줄이는 것**(20.5절의 배치)이 훨씬 효과적이에요. 반대로 14장의 언어 모델처럼 계산이 수백 ms씩 걸리는 모델이라면 모델 쪽을 줄여야 하고요. 어디를 고칠지는 이렇게 **재 보고** 정합니다.

`TestClient`는 네트워크를 거치지 않으니, 여기서 잰 것은 서버 프로그램 자체의 시간입니다. 진짜 네트워크를 거친 시간과 여러 손님이 동시에 몰릴 때의 모습은 20.11절에서 실제 서버를 띄워 재 봅니다.

## 20.10 LLM의 답을 흘려보내기: 스트리밍

### 만드는 대로 보내기

옷 분류기는 1ms 만에 답이 나오지만, 14장의 언어 모델은 토큰을 하나씩 만들어서 답 하나에 몇 초가 걸립니다. 다 만든 뒤 한꺼번에 보내면 사용자는 그동안 빈 화면만 봐요. 챗봇 서비스들이 글자가 타자 치듯 나타나게 하는 이유가 여기 있습니다. 전체 시간은 같아도 첫 글자가 빨리 보이면 기다림이 훨씬 짧게 느껴지거든요.

FastAPI의 **`StreamingResponse`** 는 1권 15장의 제너레이터를 받아서, 값이 하나 `yield`될 때마다 바로 보냅니다. 받는 쪽은 `client.stream(...)`으로 요청을 열고 `iter_text()`로 조각이 오는 대로 꺼내요. 일반 함수(`def`)로 만든 제너레이터라면 `StreamingResponse`가 20.6절의 작업 스레드에서 돌려 주니, 안에서 오래 걸리는 계산을 해도 이벤트 루프를 막지 않습니다.

### 14장 언어 모델의 답 흘려보내기

문제는 14장의 `generate`가 답을 **끝까지 다 만들어야** 돌아오는 함수라는 점이에요. `transformers`는 이를 위해 **`TextIteratorStreamer`** 를 줍니다. `generate`에 스트리머를 넘기면 토큰이 나올 때마다 글자로 바꿔 스트리머에 넣어 주고, 우리는 스트리머를 반복문으로 꺼내 읽어요. 단, `generate`는 끝날 때까지 돌아오지 않으니 **다른 스레드**(1권 17장의 `threading.Thread`)에서 돌리고, 지금 스레드에서는 스트리머를 읽습니다. 요리사가 요리하는 동안 서빙 직원이 나온 접시부터 나르는 셈이에요. 모델은 14장과 같은 Qwen2.5-0.5B-Instruct(Apache-2.0)이고, 14장처럼 CPU에서 탐욕 디코딩으로 돌렸습니다.

```python
import threading
import time
from collections.abc import Iterator
from contextlib import asynccontextmanager

import torch
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer

모델_이름 = "Qwen/Qwen2.5-0.5B-Instruct"                   # 14장의 모델


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.토크나이저 = AutoTokenizer.from_pretrained(모델_이름)
    app.state.모델 = AutoModelForCausalLM.from_pretrained(모델_이름, dtype=torch.float32).eval()
    app.state.생성_자물쇠 = threading.Lock()                   # 한 번에 한 요청만 생성
    yield


app = FastAPI(lifespan=lifespan)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    max_new_tokens: int = Field(default=60, ge=1, le=256)


def 토큰_흘리기(app: FastAPI, 요청: ChatRequest) -> Iterator[str]:
    토크나이저, 모델 = app.state.토크나이저, app.state.모델
    대화 = [{"role": "user", "content": 요청.question}]
    입력 = 토크나이저.apply_chat_template(대화, add_generation_prompt=True,
                                          return_tensors="pt", return_dict=True)
    스트리머 = TextIteratorStreamer(토크나이저, skip_prompt=True, skip_special_tokens=True)
    with app.state.생성_자물쇠:
        # generate는 끝까지 돌아야 돌아오므로 다른 스레드에서 돌리고, 나온 글자는 스트리머로 받는다
        일꾼 = threading.Thread(target=모델.generate, kwargs=dict(
            **입력, streamer=스트리머, max_new_tokens=요청.max_new_tokens, do_sample=False))
        일꾼.start()
        yield from 스트리머                                    # 조각이 나오는 대로 내보내기
        일꾼.join()


@app.post("/chat")
def 대화(요청: ChatRequest, request: Request) -> StreamingResponse:
    return StreamingResponse(토큰_흘리기(request.app, 요청), media_type="text/plain; charset=utf-8")


with TestClient(app) as client:
    시작 = time.perf_counter()
    조각들, 첫_조각 = [], None
    질문 = {"question": "파이썬의 리스트를 한 문장으로 설명해 줘.", "max_new_tokens": 60}
    with client.stream("POST", "/chat", json=질문) as 응답:
        for 조각 in 응답.iter_text():
            if 첫_조각 is None:
                첫_조각 = time.perf_counter() - 시작
            조각들.append(조각)
    전체 = time.perf_counter() - 시작
    print(f"첫 조각까지 {첫_조각:.2f}초, 전체 {전체:.2f}초, 조각 {len(조각들)}개")
    print("처음 다섯 조각:", 조각들[:5])
    print("".join(조각들))
    print(client.post("/chat", json={"question": ""}).status_code)
```

```text
첫 조각까지 0.18초, 전체 1.23초, 조각 24개
처음 다섯 조각: ['파이썬의 ', '리스트는 ', 'Python에서 ', '사용하는 ', '데이터 ']
파이썬의 리스트는 Python에서 사용하는 데이터 타입 중 하나로, 다양한 프로그래밍 패턴과 기능을 제공합니다. 리스트는 원소가 변경될 수 있는 자료형이며, 이 원소들은 순서대로 저장됩니다.

리스트의
422
```

첫 조각이 0.2초쯤에 도착했고, 60토큰짜리 답 전체는 1초 남짓 걸렸습니다(이 책의 실행 환경, CPU). 스트리밍이 없었다면 사용자는 1초를 빈 화면으로 기다렸을 거예요. 답이 길어 몇십 초씩 걸리는 경우라면 차이가 훨씬 크게 느껴집니다. 조각은 토큰 하나가 아니라 대개 **단어 하나**씩 왔어요. 스트리머가 토큰을 모아 두었다가 띄어쓰기가 나올 때 내보내기 때문입니다. 한국어 한 글자가 여러 토큰으로 쪼개지는 경우(14장 14.1절)에 깨진 글자를 보내지 않으려는 배려예요.

답은 "한 문장으로"라는 요청을 무시하고 길게 이어지다가 60토큰에서 잘렸습니다. `max_new_tokens`에 걸린 것이고, 작은 모델이 지시를 잘 따르지 못하는 것은 14장 14.5절에서 본 그대로예요. 빈 질문은 `ChatRequest`의 `min_length=1`에 걸려 422가 됐습니다.

코드에서 눈여겨볼 곳이 두 군데 있습니다.

- **`생성_자물쇠`**: `threading.Lock`은 한 번에 한 스레드만 들어갈 수 있는 자물쇠입니다. 큰 모델을 여러 스레드가 동시에 돌리면 메모리가 늘고 코어를 빼앗아 모두 느려지니, 생성은 한 번에 하나만 하고 뒤에 온 요청은 기다리게 했어요. 여러 요청을 한꺼번에 생성하는 일은 20.5절의 동적 배칭을 언어 모델에 맞게 확장한 전용 서빙 도구들의 몫입니다.
- **`yield from 스트리머`**: 1권 15장의 `yield from`으로, 스트리머가 내놓는 조각을 그대로 바깥으로 넘깁니다. 다 넘긴 뒤 `join()`으로 생성 스레드가 끝나기를 기다려요.

## 20.11 실습: 옷 사진 분류 서비스 완성하기

지금까지 만든 조각을 모아 9장 옷 분류기를 **한 벌의 서비스**로 완성하겠습니다. 역할별로 파일을 나누고(1권 14장), pytest로 시험하고, 실제 서버에 부하를 걸어 보고, Docker 이미지로 감싸는 데까지 갑니다.

### 프로젝트 구조

```text
fashion_service/
├── pyproject.toml        # 의존성 (uv)
├── uv.lock               # 정확한 버전 목록 (uv lock이 만든다)
├── .python-version       # 3.12
├── Dockerfile
├── .dockerignore
├── app/
│   ├── __init__.py       # 빈 파일 (1권 14장의 패키지 표시)
│   ├── fashion_model.py  # 9장 옷CNN 설계도와 불러오기 (torch 백엔드용)
│   ├── preprocess.py     # 사진 → (1, 28, 28) 배열
│   ├── backends.py       # ONNX / PyTorch 예측기
│   └── main.py           # FastAPI 앱
├── models/
│   ├── fashion_cnn.pt    # 9장 9.5절에서 저장한 파일
│   └── fashion_cnn.onnx  # scripts/export_onnx.py가 만든다
├── scripts/
│   ├── export_onnx.py
│   └── load_test.py
└── tests/
    ├── data/             # 시험 사진 두 장: ankle_boot.png, pullover.png
    └── test_main.py
```

`tests/data/`의 두 사진은 9장에서 쓴 FashionMNIST 시험 데이터의 0번(앵클부츠)과 1번(풀오버) 사진을 PNG로 저장한 것입니다. 9장처럼 `시험 = datasets.FashionMNIST("data", train=False)`로 불러온 뒤 `시험[0][0].save("tests/data/ankle_boot.png")`, `시험[1][0].save("tests/data/pullover.png")`를 실행하면 똑같은 파일이 만들어지고, 예제 코드 꾸러미에도 들어 있어요. `models/fashion_cnn.pt`는 9장 9.5절에서 저장한 파일을 복사해 넣으면 됩니다.

명령줄에 `app.main:app`처럼 모듈 경로를 적고 Docker로 옮길 폴더라서 파일과 폴더 이름은 영어로, 파일 **안의** 이름은 지금까지처럼 한글로 지었습니다.

`app/fashion_model.py`에는 9장의 `옷CNN` 클래스와 20.1절의 `모델_불러오기`가 들어 있습니다. 이번에는 9장 `옷도구.py`에서 `import`하지 않고 클래스를 **직접 옮겨 담았어요**. 서비스 폴더는 이 폴더만 복사해 가도 돌아가야 하니까요. 내용이 9장과 같으니 여기 다시 싣지는 않을게요.

### 전처리와 백엔드

전처리는 20.4절에서 확인한 두 가지 교훈, "학습 때와 같은 방법으로"와 "흰 배경이면 뒤집기"를 모두 담았습니다. torch 없이 NumPy와 Pillow만 써요.

```python
"""올라온 사진 파일을 모델 입력 배열로 바꾼다 (torch 없이 NumPy와 Pillow만 쓴다)."""
import io

import numpy as np
from PIL import Image, UnidentifiedImageError

최대_바이트 = 1_000_000                  # 파일 크기 한도: 1MB
최대_픽셀 = 4096 * 4096                  # 가로 × 세로 한도: 압축 폭탄 막기


class 사진오류(ValueError):
    """사진으로 읽을 수 없거나 받을 수 없는 파일."""


def 사진_전처리(데이터: bytes) -> np.ndarray:
    """사진 파일을 학습 때와 같은 (1, 28, 28) float32 배열로 바꾼다."""
    try:
        사진 = Image.open(io.BytesIO(데이터))
        if 사진.width * 사진.height > 최대_픽셀:
            raise 사진오류("사진의 가로·세로가 너무 큽니다")
        사진 = 사진.convert("L").resize((28, 28))
    except Image.DecompressionBombError as e:      # 아주 큰 그림은 Image.open이 먼저 알아채고 멈춘다
        raise 사진오류("사진의 가로·세로가 너무 큽니다") from e
    except (UnidentifiedImageError, OSError) as e:
        raise 사진오류("사진 파일이 아닙니다") from e
    배열 = np.asarray(사진, dtype=np.float32) / 255
    테두리 = np.concatenate([배열[0], 배열[-1], 배열[:, 0], 배열[:, -1]])
    if 테두리.mean() > 0.5:              # 배경이 밝으면 뒤집어서 학습 데이터처럼 검은 배경으로
        배열 = 1 - 배열
    return 배열[None]
```

20.4절에서 하지 않던 검사가 하나 늘었습니다. PNG 같은 형식은 압축이 잘되는 그림을 아주 작은 파일에 담을 수 있어서, 1MB 한도를 통과한 파일이 열어 보니 수만 × 수만 픽셀이라 메모리를 다 먹어 버리는 공격(압축 폭탄)이 가능해요. `Image.open`은 파일 머리말만 읽고 실제 픽셀은 아직 풀지 않으니, 그 사이에 가로 × 세로를 확인해 막았습니다. 가로 × 세로가 터무니없이 크면(약 1억 8천만 픽셀이 넘으면) Pillow가 `Image.open`에서 먼저 `DecompressionBombError`를 내며 멈추는데, 이 오류는 `OSError`가 아니라서 따로 잡아 같은 `사진오류`로 바꿨어요. 잡지 않으면 500이 나갑니다. 전처리에서 난 문제는 HTTP를 모르는 `사진오류`로 던지고, 상태 코드로 바꾸는 일은 `main.py`에 맡겼어요. 전처리 함수를 HTTP 없이도 쓰고 시험할 수 있게요.

```python
"""모델 계산을 맡는 백엔드: 같은 약속(점수)을 지키는 두 가지 구현."""
import os
from pathlib import Path
from typing import Protocol

import numpy as np


class 예측기(Protocol):
    """(N, 1, 28, 28) float32 배열을 받아 (N, 10) 점수를 돌려준다."""
    이름: str
    모델_파일: Path

    def 점수(self, x: np.ndarray) -> np.ndarray: ...


class ONNX예측기:
    이름 = "onnx"

    def __init__(self, 폴더: Path) -> None:
        import onnxruntime as ort

        self.모델_파일 = 폴더 / "fashion_cnn.onnx"
        옵션 = ort.SessionOptions()
        옵션.intra_op_num_threads = int(os.environ.get("ORT_THREADS", "0"))   # 0이면 코어 수만큼
        self.세션 = ort.InferenceSession(self.모델_파일, 옵션, providers=["CPUExecutionProvider"])

    def 점수(self, x: np.ndarray) -> np.ndarray:
        return self.세션.run(["logits"], {"image": x})[0]


class 파이토치예측기:
    이름 = "torch"

    def __init__(self, 폴더: Path) -> None:
        import torch                            # torch 백엔드를 고를 때만 필요하다

        from app.fashion_model import 모델_불러오기

        self.모델_파일 = 폴더 / "fashion_cnn.pt"
        self.torch, self.모델 = torch, 모델_불러오기(self.모델_파일)

    def 점수(self, x: np.ndarray) -> np.ndarray:
        with self.torch.no_grad():
            return self.모델(self.torch.from_numpy(x)).numpy()


def 예측기_만들기(이름: str, 폴더: Path) -> 예측기:
    백엔드들 = {"onnx": ONNX예측기, "torch": 파이토치예측기}
    if 이름 not in 백엔드들:
        raise ValueError(f"알 수 없는 백엔드: {이름} (가능: {', '.join(백엔드들)})")
    return 백엔드들[이름](폴더)
```

20.8절에서 말한 약속을 코드로 옮긴 파일입니다.

- **`예측기(Protocol)`**: 1권 13장의 `Protocol`로 약속을 적었습니다. `이름`, `모델_파일`, 그리고 배열을 받아 배열을 돌려주는 `점수`. 두 백엔드 클래스는 `예측기`를 상속하지 않고 이 셋을 갖추기만 했어요. `Protocol`은 실행할 때 검사하는 것이 아니라 읽는 사람과 타입 검사 도구를 위한 약속이라, 뒤의 테스트에서는 경로 함수가 실제로 부르는 `점수`만 갖춘 가짜도 끼워 쓸 수 있습니다.
- **`import`를 클래스 안에서**: `onnxruntime`과 `torch`를 파일 맨 위가 아니라 각 클래스의 `__init__` 안에서 불러옵니다. 그 백엔드를 고를 때만 그 라이브러리가 필요하니, ONNX만 쓰는 서버는 PyTorch를 깔지 않아도 이 파일을 불러올 수 있어요.
- **`예측기_만들기`**: 이름으로 백엔드를 고릅니다. 모르는 이름이면 서버가 시작될 때 바로 오류를 내서, 설정 실수를 손님이 오기 전에 알게 해요.
- **`ORT_THREADS`**: ONNX Runtime이 계산에 쓸 스레드 수를 환경 변수로 정할 수 있게 했습니다. 기본값 0은 "알아서 코어 수만큼"이에요. 이 손잡이가 왜 필요한지는 조금 뒤 부하 시험에서 보여 드릴게요.

### 경로 함수

```python
"""옷 사진 분류 서비스: 9장 옷CNN을 HTTP로 내놓는다."""
import hashlib
import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

import numpy as np
from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from pydantic import BaseModel

from app.backends import 예측기, 예측기_만들기
from app.preprocess import 사진_전처리, 사진오류, 최대_바이트

앱_버전 = "1.0.0"
최대_장수 = 32
클래스_이름 = ["T셔츠", "바지", "풀오버", "드레스", "코트",
          "샌들", "셔츠", "운동화", "가방", "앵클부츠"]
로그 = logging.getLogger("uvicorn.error")            # uvicorn이 찍는 로그에 함께 나오게


class ClassScore(BaseModel):
    label: str
    probability: float


class Prediction(BaseModel):
    file: str
    label: str
    class_id: int
    probability: float
    top3: list[ClassScore]


@asynccontextmanager
async def lifespan(app: FastAPI):
    백엔드 = os.environ.get("MODEL_BACKEND", "onnx")
    폴더 = Path(os.environ.get("MODEL_DIR", "models"))
    app.state.예측기 = 예측기_만들기(백엔드, 폴더)
    app.state.모델_지문 = hashlib.sha256(app.state.예측기.모델_파일.read_bytes()).hexdigest()[:12]
    로그.info("모델 준비 완료: backend=%s, sha256=%s", 백엔드, app.state.모델_지문)
    yield


app = FastAPI(title="옷 사진 분류 API", version=앱_버전, lifespan=lifespan)


@app.middleware("http")
async def 처리_시간_기록(request: Request, call_next):
    시작 = time.perf_counter()
    응답 = await call_next(request)
    응답.headers["X-Process-Time-ms"] = f"{(time.perf_counter() - 시작) * 1000:.2f}"
    return 응답


def 예측기_얻기(request: Request) -> 예측기:
    """경로 함수가 쓸 예측기. 테스트에서는 이 함수를 가짜로 바꿔 끼운다."""
    return request.app.state.예측기


def 파일_읽기(file: UploadFile) -> np.ndarray:
    데이터 = file.file.read(최대_바이트 + 1)
    if len(데이터) > 최대_바이트:
        raise HTTPException(status_code=413, detail=f"{file.filename}: 1MB보다 큽니다")
    try:
        return 사진_전처리(데이터)
    except 사진오류 as e:
        raise HTTPException(status_code=400, detail=f"{file.filename}: {e}")


def 결과_만들기(이름들: list[str], 점수: np.ndarray) -> list[Prediction]:
    확률 = np.exp(점수 - 점수.max(axis=1, keepdims=True))      # 소프트맥스 (6장)
    확률 /= 확률.sum(axis=1, keepdims=True)
    결과 = []
    for 이름, p in zip(이름들, 확률):
        상위 = [ClassScore(label=클래스_이름[i], probability=round(float(p[i]), 4))
                for i in p.argsort()[::-1][:3]]
        결과.append(Prediction(file=이름, label=상위[0].label, class_id=int(p.argmax()),
                               probability=상위[0].probability, top3=상위))
    return 결과


@app.get("/health")
def 살아있나() -> dict:
    return {"status": "ok"}


@app.get("/version")
def 버전(request: Request) -> dict:
    예측기_ = request.app.state.예측기
    return {"app": 앱_버전, "backend": 예측기_.이름, "model_file": 예측기_.모델_파일.name,
            "model_sha256": request.app.state.모델_지문}


@app.post("/predict/image")
def 사진_예측(file: UploadFile = File(...), 예측기_: 예측기 = Depends(예측기_얻기)) -> Prediction:
    x = 파일_읽기(file)[None]                                  # (1, 1, 28, 28)
    return 결과_만들기([file.filename or ""], 예측기_.점수(x))[0]


@app.post("/predict/batch")
def 여러_장_예측(files: list[UploadFile] = File(...),
                예측기_: 예측기 = Depends(예측기_얻기)) -> list[Prediction]:
    if len(files) > 최대_장수:
        raise HTTPException(status_code=413, detail=f"한 번에 {최대_장수}장까지 보낼 수 있습니다")
    x = np.stack([파일_읽기(f) for f in files])                # (N, 1, 28, 28)
    return 결과_만들기([f.filename or "" for f in files], 예측기_.점수(x))
```

20.2절부터 20.7절까지의 조각이 모두 들어 있습니다. 새로 달라진 곳만 짚어 볼게요.

- **설정은 환경 변수로**: 백엔드(`MODEL_BACKEND`, 기본 onnx)와 모델 폴더(`MODEL_DIR`, 기본 `models`)를 코드 밖에서 정합니다. Docker로 띄울 때 이 값을 바꿔 줄 수 있어요.
- **로그**: 1권 19장에서는 확인용으로 `print`를 썼지만, 서버에서는 `logging`을 씁니다. `uvicorn.error`는 uvicorn이 자기 메시지를 찍는 로거의 이름이에요(이름과 달리 오류만 찍는 곳은 아닙니다). 여기에 쓰면 uvicorn의 `INFO:` 로그 사이에 함께 나옵니다.
- **`Depends(예측기_얻기)`**: 20.2~20.7절에서는 경로 함수가 `request.app.state`에서 모델을 직접 꺼냈는데, 이번에는 꺼내는 일을 의존성 함수(1권 19.4절)로 뺐습니다. 이렇게 해 두면 테스트에서 이 함수만 **가짜로 바꿔 끼울 수** 있어요. 바로 다음에 씁니다.
- **소프트맥스는 NumPy로**: 백엔드가 점수만 돌려주니 확률은 직접 계산했습니다. 가장 큰 점수를 먼저 빼는 것은 6장 6.2절에서 `torch.softmax`가 안에서 쓴다고 했던, `exp`가 넘치지 않게 하는 요령 그대로예요.
- **배치 상한**: 32장을 넘으면 413, 파일마다 1MB가 넘으면 413, 사진이 아니면 400. 오류 메시지에 파일 이름을 넣어서 여러 장 중 어느 파일이 문제인지 알 수 있게 했습니다.

### ONNX 파일 만들기

서비스는 ONNX 파일로 돌지만, 그 파일은 PyTorch가 있어야 만들 수 있습니다. 내보내기와 확인을 스크립트 하나로 묶어 두면, 모델을 다시 학습할 때마다 같은 방법으로 만들 수 있어요.

```python
"""models/fashion_cnn.pt를 ONNX로 내보내고, 두 결과가 같은지 확인한다."""
from pathlib import Path

import numpy as np
import onnxruntime as ort
import torch

from app.fashion_model import 모델_불러오기

폴더 = Path("models")
모델 = 모델_불러오기(폴더 / "fashion_cnn.pt")
배치 = torch.export.Dim("batch", min=1, max=1024)
torch.onnx.export(모델, (torch.zeros(1, 1, 28, 28),), 폴더 / "fashion_cnn.onnx", dynamo=True,
                  input_names=["image"], output_names=["logits"], dynamic_shapes={"x": {0: 배치}},
                  external_data=False, verbose=False)

x = torch.rand(16, 1, 28, 28, generator=torch.Generator().manual_seed(0))
with torch.no_grad():
    기대값 = 모델(x).numpy()
세션 = ort.InferenceSession(폴더 / "fashion_cnn.onnx", providers=["CPUExecutionProvider"])
오차 = np.abs(세션.run(["logits"], {"image": x.numpy()})[0] - 기대값).max()
assert 오차 < 1e-4, f"PyTorch와 ONNX 결과가 다릅니다: {오차}"
print(f"내보내기 완료: {폴더 / 'fashion_cnn.onnx'} (최대 오차 {오차:.1e})")
```

내보낸 뒤 PyTorch와 ONNX Runtime에 같은 사진 16장을 넣어 보고, 차이가 0.0001을 넘으면 `assert`로 멈춥니다. 잘못 만든 파일이 서비스에 올라가는 것을 이 자리에서 막는 거예요. 프로젝트 폴더에서 이렇게 실행합니다. `--extra torch`는 `pyproject.toml`의 선택 의존성(바로 뒤에 봅니다)까지 설치하라는 뜻이고, `-m scripts.export_onnx`로 실행해야 스크립트 안에서 `app` 패키지를 찾을 수 있어요.

```bash
uv run --extra torch python -m scripts.export_onnx
```

```text
내보내기 완료: models/fashion_cnn.onnx (최대 오차 3.8e-06)
```

실행하면 이 줄 앞에 "torchvision이 설치되어 있지 않아 일부 연산 등록을 건너뛴다"는 경고가 몇 줄 나오는데, 우리 모델은 torchvision 연산을 쓰지 않으니 무시해도 됩니다.

### 테스트: 진짜 모델과 가짜 모델

이제 서비스가 약속대로 동작하는지 pytest로 확인하겠습니다. 1권 13장에서 `test_`로 시작하는 함수의 `assert`를 pytest가 모아 실행한다고 했죠. 여기서는 pytest의 **픽스처(fixture)** 를 하나 더 씁니다. `@pytest.fixture`를 붙인 함수를 테스트 함수의 매개변수 이름으로 적으면, pytest가 그 함수를 실행해 결과를 넣어 줘요. FastAPI의 `Depends`와 비슷한 생각입니다. 픽스처 안에서 `yield`를 쓰면 `yield` 뒤는 테스트가 끝난 뒤에 실행되니 정리 작업도 넣을 수 있고요.

테스트를 두 종류로 나눴습니다.

- **진짜 모델로**: 실제 ONNX 파일로 앵클부츠·풀오버 사진을 맞히는지, 흰 배경 사진도 맞히는지 확인합니다. 모델과 전처리가 함께 제대로 도는지 보는 테스트예요.
- **가짜 모델로**: 언제나 "드레스"라고 답하는 `가짜예측기`를 끼우고, 응답 모양과 오류 처리를 확인합니다. 모델 파일이 바뀌어도 결과가 흔들리지 않고, 모델이 무거워도 빨리 돌아요. `app.dependency_overrides[예측기_얻기] = 가짜예측기`가 "`예측기_얻기`를 의존하는 곳에는 가짜를 넣어라"라는 뜻입니다.

```python
"""옷 사진 분류 API 테스트. 실행: uv run --extra torch pytest -q"""
import io
from collections.abc import Iterator
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageOps

from app.main import app, 예측기_얻기

자료 = Path(__file__).parent / "data"


class 가짜예측기:
    """언제나 3번(드레스)이 가장 높은 점수를 내는 가짜. 모델 없이 API 모양만 시험한다."""
    이름 = "fake"

    def 점수(self, x: np.ndarray) -> np.ndarray:
        점수 = np.zeros((len(x), 10), dtype=np.float32)
        점수[:, 3] = 5.0
        return 점수


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:                       # with로 열어야 lifespan이 돈다
        yield c


@pytest.fixture
def fake_client(client: TestClient) -> Iterator[TestClient]:
    app.dependency_overrides[예측기_얻기] = 가짜예측기  # 진짜 대신 가짜를 끼운다
    yield client
    app.dependency_overrides.clear()                 # 다른 테스트에 번지지 않게 되돌린다


def 사진_파일(이름: str) -> tuple[str, bytes]:
    return 이름, (자료 / 이름).read_bytes()


def test_health_and_version_after_startup(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/version").json()["backend"] == "onnx"


def test_predict_image_with_real_model_returns_correct_label(client: TestClient) -> None:
    for 이름, 정답 in [("ankle_boot.png", "앵클부츠"), ("pullover.png", "풀오버")]:
        응답 = client.post("/predict/image", files={"file": 사진_파일(이름)})
        assert 응답.status_code == 200
        assert 응답.json()["label"] == 정답
        assert "x-process-time-ms" in 응답.headers


def test_predict_image_with_white_background_still_correct(client: TestClient) -> None:
    사진 = ImageOps.invert(Image.open(자료 / "ankle_boot.png"))     # 흰 배경으로 뒤집은 사진
    버퍼 = io.BytesIO()
    사진.save(버퍼, format="PNG")
    응답 = client.post("/predict/image", files={"file": ("white.png", 버퍼.getvalue())})
    assert 응답.json()["label"] == "앵클부츠"


def test_predict_image_with_fake_model_returns_response_shape(fake_client: TestClient) -> None:
    본문 = fake_client.post("/predict/image", files={"file": 사진_파일("pullover.png")}).json()
    assert 본문["label"] == "드레스" and 본문["class_id"] == 3
    assert len(본문["top3"]) == 3
    assert sum(항목["probability"] for 항목 in 본문["top3"]) <= 1.0


def test_predict_image_when_not_image_returns_400(fake_client: TestClient) -> None:
    응답 = fake_client.post("/predict/image", files={"file": ("memo.txt", b"hello")})
    assert 응답.status_code == 400
    assert "사진 파일이 아닙니다" in 응답.json()["detail"]


def test_predict_image_when_too_large_returns_413(fake_client: TestClient) -> None:
    응답 = fake_client.post("/predict/image", files={"file": ("big.png", bytes(1_000_001))})
    assert 응답.status_code == 413


def test_predict_batch_keeps_order_and_limits_count(fake_client: TestClient) -> None:
    두_장 = [("files", 사진_파일("ankle_boot.png")), ("files", 사진_파일("pullover.png"))]
    본문 = fake_client.post("/predict/batch", files=두_장).json()
    assert [항목["file"] for 항목 in 본문] == ["ankle_boot.png", "pullover.png"]
    서른세_장 = [("files", 사진_파일("pullover.png"))] * 33
    assert fake_client.post("/predict/batch", files=서른세_장).status_code == 413


def test_backends_torch_and_onnx_agree() -> None:
    pytest.importorskip("torch")                     # torch가 없는 환경에서는 건너뛴다
    from app.backends import 예측기_만들기
    from app.preprocess import 사진_전처리

    파일들 = ["ankle_boot.png", "pullover.png"]
    x = np.stack([사진_전처리((자료 / 이름).read_bytes()) for 이름 in 파일들])
    점수들 = [예측기_만들기(이름, Path("models")).점수(x) for 이름 in ["torch", "onnx"]]
    assert np.abs(점수들[0] - 점수들[1]).max() < 1e-4
```

테스트 이름은 "무엇을, 어떤 상황에서, 어떻게 되어야 하는가"가 드러나게 지어서, 실패하면 이름만 보고 어디가 깨졌는지 알 수 있게 했습니다. 마지막 테스트는 torch 백엔드와 ONNX 백엔드의 점수가 같은지 보는데, torch가 설치되지 않은 환경에서는 `pytest.importorskip`이 이 테스트를 실패가 아니라 **건너뜀**으로 처리합니다. 실행해 보겠습니다.

```bash
uv run --extra torch pytest -q
```

```text
........                                                                 [100%]
8 passed in 1.05s
```

점 여덟 개가 테스트 여덟 개의 통과를 뜻합니다. 실패한 테스트가 있으면 점 대신 `F`가 찍히고, 아래에 어느 `assert`에서 무엇이 달랐는지 자세히 나와요.

### 서버로 띄우기

테스트를 통과했으니 진짜 서버를 띄워 보겠습니다. 터미널 하나에서 서버를 띄우고,

```bash
uv run uvicorn app.main:app --port 8000
```

다른 터미널에서 `curl`로 요청을 보냅니다. `curl`은 맥과 리눅스, 윈도우 10 이상에 기본으로 들어 있는 명령줄 HTTP 도구예요. `-F "file=@경로"`는 파일을 multipart로 올리라는 뜻입니다.

```bash
curl -s localhost:8000/version
curl -s -F "file=@tests/data/ankle_boot.png" localhost:8000/predict/image
curl -s -i -F "files=@tests/data/ankle_boot.png" -F "files=@tests/data/pullover.png" localhost:8000/predict/batch
```

```text
{"app":"1.0.0","backend":"onnx","model_file":"fashion_cnn.onnx","model_sha256":"265e35c606cf"}
{"file":"ankle_boot.png","label":"앵클부츠","class_id":9,"probability":0.9973,"top3":[{"label":"앵클부츠","probability":0.9973},{"label":"운동화","probability":0.0025},{"label":"샌들","probability":0.0002}]}
HTTP/1.1 200 OK
date: Wed, 21 Oct 2026 07:01:33 GMT
server: uvicorn
content-length: 430
content-type: application/json
x-process-time-ms: 1.51

[{"file":"ankle_boot.png","label":"앵클부츠","class_id":9,"probability":0.9973,"top3":[{"label":"앵클부츠","probability":0.9973},{"label":"운동화","probability":0.0025},{"label":"샌들","probability":0.0002}]},{"file":"pullover.png","label":"풀오버","class_id":2,"probability":0.9998,"top3":[{"label":"풀오버","probability":0.9998},{"label":"T셔츠","probability":0.0001},{"label":"셔츠","probability":0.0}]}]
```

`/version`의 모델 지문이 20.7절과 다르죠? 그때는 `.pt` 파일의 해시였고 지금은 `.onnx` 파일의 해시라서 그렇습니다. 같은 모델이라도 파일이 다르면 지문이 다르니, 지문과 함께 파일 이름도 알려 주는 것이 좋아요. 세 번째 요청은 `-i`로 응답 헤더까지 보이게 했는데, 미들웨어가 붙인 `x-process-time-ms`가 보입니다. 서버를 띄운 터미널에는 이런 로그가 찍혀요. 마지막 네 줄은 요청을 다 보낸 뒤 서버를 끌 때(`Ctrl+C`) 나온 것입니다.

```text
INFO:     Started server process [58418]
INFO:     Waiting for application startup.
INFO:     모델 준비 완료: backend=onnx, sha256=265e35c606cf
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:58890 - "GET /version HTTP/1.1" 200 OK
INFO:     127.0.0.1:58892 - "POST /predict/image HTTP/1.1" 200 OK
INFO:     127.0.0.1:58894 - "POST /predict/batch HTTP/1.1" 200 OK
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [58418]
```

`Waiting for application startup`과 `Application startup complete` 사이에 우리 lifespan의 로그가 찍혔습니다. uvicorn은 lifespan의 `yield` 앞부분이 끝나야 손님을 받기 시작해요. 마지막 `Uvicorn running on` 줄도 lifespan 뒤에 찍혔죠? 모델이 다 올라온 뒤에야 포트를 열어 손님을 받는다는 뜻이라, 20.7절의 `/ready`가 503을 내는 순간이 uvicorn에서는 생기지 않습니다. 그 대신 모델이 커서 시작이 오래 걸리면 그동안은 포트가 아예 닫혀 있으니, 감시 프로그램이 '응답 없음'으로 오해하지 않게 시작에 걸리는 시간을 알려 줘야 해요(Docker의 `HEALTHCHECK`라면 `--start-period` 옵션). 끌 때는 `Waiting for application shutdown` 줄에서 lifespan의 `yield` 뒷부분이 실행돼요.

### 부하를 걸어 보기

손님이 한 명씩 올 때와 여럿이 몰릴 때는 어떻게 다를까요? 서버에 동시에 요청을 보내는 작은 스크립트를 만들었습니다. 20.5절의 `asyncio.gather`로 "손님" 코루틴 여러 개를 동시에 돌리고, 손님마다 번호표가 떨어질 때까지 요청을 계속 보내요. `TestClient`가 쓰는 `httpx2`의 비동기 클라이언트로 진짜 네트워크 요청을 보냅니다.

```python
"""서버에 동시에 요청을 보내 처리량과 지연 시간을 잰다. 인자: 주소 [동시 손님 수] [총 요청 수]"""
import asyncio
import statistics
import sys
import time
from pathlib import Path

import httpx2


async def 부하_주기(주소: str, 동시: int, 총: int) -> None:
    사진 = Path("tests/data/ankle_boot.png").read_bytes()
    걸린_시간: list[float] = []
    남은_번호 = iter(range(총))

    async def 손님(client: httpx2.AsyncClient) -> None:
        for _ in 남은_번호:                          # 번호표가 떨어질 때까지 계속 요청
            시작 = time.perf_counter()
            응답 = await client.post("/predict/image", files={"file": ("x.png", 사진)})
            응답.raise_for_status()
            걸린_시간.append((time.perf_counter() - 시작) * 1000)

    async with httpx2.AsyncClient(base_url=주소, timeout=10) as client:
        시작 = time.perf_counter()
        await asyncio.gather(*[손님(client) for _ in range(동시)])
        전체 = time.perf_counter() - 시작
    백분위 = statistics.quantiles(걸린_시간, n=100)
    print(f"동시 {동시}명, 요청 {총}개: 초당 {총 / 전체:,.0f}개, "
          f"p50 {백분위[49]:.1f}ms, p95 {백분위[94]:.1f}ms, p99 {백분위[98]:.1f}ms")


if __name__ == "__main__":
    주소 = sys.argv[1]
    동시 = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    총 = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
    asyncio.run(부하_주기(주소, 동시, 총))
```

서버를 띄워 둔 채로 `uv run python -m scripts.load_test http://127.0.0.1:8000 16 3000`처럼 실행합니다(동시 손님 16명, 요청 3,000개). uvicorn의 `--workers` 옵션으로 서버 프로세스 수를, 환경 변수 `ORT_THREADS`로 ONNX Runtime의 계산 스레드 수를 바꿔 가며 쟀습니다. 아래는 이 책의 실행 환경(Apple M4 Max, 코어 16개)에서 잰 값이에요. 같은 컴퓨터에서 부하를 주는 프로그램도 함께 돌았으니 절대값보다는 서로의 비교로 보세요.

```bash
ORT_THREADS=1 uv run uvicorn app.main:app --port 8000 --workers 4
```

| 서버 설정 | 동시 1명: 초당 요청 | 동시 1명: p99 | 동시 16명: 초당 요청 | 동시 16명: p50 | 동시 16명: p99 |
|---|---|---|---|---|---|
| 워커 1개, 스레드 기본값 | 656 | 1.8ms | 1,424 | 10.9ms | 19.2ms |
| 워커 1개, 스레드 1개 | 611 | 1.9ms | 1,377 | 11.3ms | 20.2ms |
| 워커 4개, 스레드 기본값 | 643 | 2.5ms | 699 | 21.7ms | 43.1ms |
| 워커 4개, 스레드 1개 | 613 | 1.9ms | 2,065 | 7.4ms | 13.4ms |

표에서 세 가지를 읽을 수 있습니다.

- **손님이 한 명이면 설정은 상관없습니다.** 어느 설정이든 초당 600개 남짓, p99도 2.5ms 안쪽이에요. 한 번에 요청 하나뿐이니 워커와 스레드를 늘려도 놉니다.
- **손님이 몰리면 줄이 생깁니다.** 워커 하나로 16명을 받으면 초당 1,400개쯤에서 막히고 중앙값 지연이 11ms로 늘었어요. 늘어난 것은 **줄 서서 기다리는 시간**입니다.
- **워커를 늘렸더니 오히려 느려졌습니다.** 워커 네 개에 스레드를 기본값으로 두니 초당 699개로 워커 하나일 때의 절반이 됐어요. 프로세스 네 개가 저마다 "코어 수만큼" 스레드를 만들어 모두 16개 코어를 차지하려고 다투면서, 계산보다 자리다툼에 시간을 쓴 겁니다. 이런 상태를 **과다 구독(oversubscription)** 이라고 해요. 프로세스마다 스레드를 하나로 줄이자 초당 2,065개, p99 13.4ms로 가장 좋아졌습니다.

20.6절에서 본 것처럼 PyTorch와 ONNX Runtime은 스스로 코어를 나눠 쓰니, 그 위에 프로세스나 스레드를 더 얹을 때는 **곱한 수가 코어 수를 넘지 않게** 맞춰야 해요. 그래서 다음에 만들 Docker 이미지에는 `ORT_THREADS=1`을 기본으로 넣었습니다. 몇 개의 워커가 가장 좋은지는 모델과 컴퓨터마다 다르니, 이 스크립트로 직접 재서 정하세요.

### Docker로 감싸기

이제 서비스를 회사 서버나 클라우드로 옮겨야 합니다. 그 컴퓨터에는 파이썬 3.12가 없을 수도, 다른 버전의 numpy가 깔려 있을 수도, 운영체제가 리눅스일 수도 있어요. "내 컴퓨터에서는 되는데요"가 나오는 순간이죠.

**Docker**는 이 문제를 이사 비유로 풉니다. 짐을 하나하나 새집에 맞춰 다시 사는 대신, 방 하나를 통째로 **컨테이너**에 담아 옮기는 거예요. 운영체제의 필요한 부분, 파이썬, 패키지, 우리 코드, 모델 파일까지 한 상자에 담으니 어느 컴퓨터에 내려놓아도 똑같이 돕니다. 용어 두 개만 알면 돼요.

- **이미지(image)**: 상자의 설계도이자 완성품입니다. `Dockerfile`이라는 글 파일에 "무엇을 어떤 순서로 담을지" 적으면 `docker build`가 이미지를 만들어요. 한 번 만든 이미지는 바뀌지 않습니다.
- **컨테이너(container)**: 이미지를 실제로 실행한 것입니다. 이미지 하나로 컨테이너를 여러 개 띄울 수 있어요. 클래스(이미지)와 객체(컨테이너)의 관계와 비슷합니다(1권 11장).

Docker는 docker.com에서 Docker Desktop을 받아 설치하면 됩니다. 먼저 의존성을 정리한 `pyproject.toml`을 보겠습니다.

```toml
[project]
name = "fashion-service"
version = "1.0.0"
requires-python = ">=3.12"
dependencies = [            # 서빙에 꼭 필요한 것만 (torch 없음)
    "fastapi>=0.156",
    "uvicorn>=0.54",
    "python-multipart>=0.0.32",
    "numpy>=2.5",
    "pillow>=13.0",
    "onnxruntime>=1.31",
]

[project.optional-dependencies]
torch = ["torch>=2.14", "onnx>=1.23", "onnxscript>=0.7"]   # torch 백엔드와 ONNX 내보내기용

[dependency-groups]
dev = ["pytest>=8.4", "httpx2>=2.15"]     # httpx2: TestClient가 쓰는 HTTP 라이브러리

[tool.uv]
package = false             # 설치할 패키지가 아니라 실행할 앱이다

[tool.pytest.ini_options]
pythonpath = ["."]          # 테스트에서 app 패키지를 찾을 수 있게

# 리눅스(도커)에서는 CUDA가 빠진 CPU 전용 torch를 받는다
[[tool.uv.index]]
name = "pytorch-cpu"
url = "https://download.pytorch.org/whl/cpu"
explicit = true

[tool.uv.sources]
torch = [{ index = "pytorch-cpu", marker = "sys_platform == 'linux'" }]
```

이 파일이 이미지 크기를 좌우합니다.

- **`dependencies`에는 서빙에 꼭 필요한 것만**: FastAPI, uvicorn, 업로드용 python-multipart, NumPy, Pillow, ONNX Runtime. **torch가 없습니다.**
- **torch는 선택 의존성으로**: `[project.optional-dependencies]`의 `torch` 묶음은 `--extra torch`를 줄 때만 설치됩니다. ONNX 내보내기와 torch 백엔드에만 필요하니까요.
- **테스트 도구는 개발 그룹으로**: `[dependency-groups]`의 `dev`는 `uv run`이 개발할 때 기본으로 설치하고, Docker 이미지를 만들 때는 `--no-dev`로 뺍니다.
- **리눅스용 torch는 CPU 전용으로**: 마지막 두 표는 "리눅스에서는 torch를 PyTorch의 CPU 전용 저장소에서 받으라"는 설정입니다. 왜 필요한지는 조금 뒤 이미지 크기로 보여 드릴게요. `explicit = true`는 torch 말고 다른 패키지는 이 저장소에서 찾지 말라는 뜻입니다.

`uv lock`을 실행하면 이 조건을 만족하는 정확한 버전이 `uv.lock`에 기록됩니다. 이미지 안에서 같은 잠금 파일로 설치하니, 내 노트북과 똑같은 버전이 들어가요(18장의 재현성). 이제 `Dockerfile`입니다.

```dockerfile
# 1단계: uv로 가상 환경을 만든다 (빌드 도구는 이 단계에만 있다)
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.9.16 /uv /bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ARG EXTRAS=""
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev $EXTRAS

# 2단계: 실행에 필요한 것만 옮겨 담는다
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY app ./app
COPY models ./models
ENV PATH="/app/.venv/bin:$PATH" MODEL_BACKEND=onnx ORT_THREADS=1
USER nobody
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`FROM`이 두 번 나옵니다. **다단계 빌드(multi-stage build)** 라고 해요.

- **1단계(`builder`)**: 파이썬 3.12가 들어 있는 가벼운 리눅스 이미지(`python:3.12-slim`)에서 시작해, uv 공식 이미지에서 `uv` 실행 파일만 복사해 옵니다. `pyproject.toml`과 `uv.lock`을 먼저 복사해서 `uv sync --frozen --no-dev`로 가상 환경을 만들어요. `--frozen`은 잠금 파일을 고치지 말고 적힌 그대로 설치하라는 뜻입니다. `ARG EXTRAS`는 빌드할 때 `--extra torch`를 끼워 넣을 수 있게 열어 둔 자리예요.
- **2단계**: 새 `python:3.12-slim`에서 다시 시작해, 1단계에서 만든 **가상 환경 폴더만** 복사해 옵니다. uv와 설치 중에 쌓인 캐시는 1단계에 두고 오니 최종 이미지가 가벼워져요. 그다음 코드와 모델을 복사합니다.

나머지 줄도 하나씩 이유가 있습니다.

- **복사 순서**: Docker는 줄마다 결과를 **층(layer)** 으로 저장해 두고 바뀌지 않은 줄은 다음 빌드에서 그대로 씁니다. 잘 바뀌지 않는 의존성 설치를 먼저, 자주 바뀌는 코드 복사를 나중에 두면 코드만 고쳤을 때 설치를 건너뛰어요.
- **`ENV`**: 가상 환경의 `bin`을 `PATH` 앞에 넣어 `uvicorn`과 `python`이 가상 환경 것으로 실행되게 하고, 백엔드와 스레드 수의 기본값을 정합니다. `docker run -e MODEL_BACKEND=...`로 바꿀 수 있어요.
- **`USER nobody`**: 서버를 관리자(root)가 아닌, 아무 권한 없는 사용자로 실행합니다. 서버에 구멍이 나도 피해를 줄이는 기본 습관이에요.
- **`HEALTHCHECK`**: Docker가 30초마다 컨테이너 안에서 `/health`를 불러 봅니다. 응답이 없으면 컨테이너 상태가 `unhealthy`로 바뀌어요. 20.7절의 헬스 체크를 쓰는 곳이 바로 여기입니다. 이미지에 `curl`이 없어서 파이썬 표준 라이브러리의 `urllib`로 불렀어요.
- **`CMD`**: 컨테이너가 시작될 때 실행할 명령입니다. `--host 0.0.0.0`이 중요해요. 기본값 `127.0.0.1`은 "같은 컨테이너 안에서 온 요청만 받는다"는 뜻이라, 컨테이너 밖에서는 접속할 수 없습니다.

`.dockerignore`에는 이미지에 넣지 않을 것을 적습니다. 특히 내 노트북의 `.venv`가 들어가면 맥용 패키지가 리눅스 이미지에 섞이니 꼭 빼야 해요.

```text
.venv
__pycache__
.pytest_cache
tests
scripts
```

이제 빌드합니다. `-t`는 이미지에 붙일 이름표(이름:태그)예요. 비교를 위해 torch를 넣은 이미지도 함께 만들었습니다.

```bash
docker build -t fashion-service:onnx .
docker build --build-arg EXTRAS="--extra torch" -t fashion-service:torch-cpu .
docker images fashion-service
```

```text
REPOSITORY        TAG         IMAGE ID       CREATED                  SIZE
fashion-service   torch-cpu   d795993dd16f   Less than a second ago   1.51GB
fashion-service   onnx        9af313c3c83e   1 second ago             445MB
fashion-service   torch       b626eed4c12e   17 minutes ago           9.22GB
```

목록에 이미지가 셋 있습니다. 세 번째 `torch`는 `pyproject.toml`에 CPU 전용 저장소 설정을 넣기 **전에** 같은 방법으로 만든 이미지예요. 크기를 비교해 보세요.

| 이미지 | 들어 있는 것 | 크기 |
|---|---|---|
| `fashion-service:onnx` | ONNX Runtime만 | 445MB |
| `fashion-service:torch-cpu` | + CPU 전용 PyTorch | 1.51GB |
| `fashion-service:torch` | + 보통 PyTorch (CUDA 라이브러리 포함) | 9.22GB |

리눅스용 PyTorch를 그냥 설치하면 NVIDIA GPU용 CUDA 라이브러리가 함께 따라와서 이미지가 9GB를 넘었습니다. 빌드 기록을 보면 `nvidia-`로 시작하는 패키지가 줄줄이 설치돼요. GPU가 없는 서버에는 쓸모없는 짐이죠. CPU 전용 저장소에서 받으니 1.51GB로 줄었고, PyTorch를 아예 빼고 ONNX Runtime만 넣으니 445MB입니다. 같은 일을 하는 서비스가 스무 배 차이 나는 거예요. 이미지가 작으면 서버로 내려받는 시간, 저장 공간, 새 서버를 띄우는 시간이 모두 줄어듭니다. 19장에서 ONNX로 내보낸 수고가 여기서 보상받는 셈이에요.

`docker images`로 보면 바탕 이미지 `python:3.12-slim`만 해도 203MB이니, ONNX 이미지에서 우리 몫은 절반 남짓입니다. 컨테이너 안에서 `du`로 재 보니 가상 환경 폴더가 ONNX 이미지는 170MB, torch-cpu 이미지는 979MB였어요.

이제 ONNX 이미지로 컨테이너를 띄워 봅니다.

```bash
docker run -d --name fashion -p 8000:8000 fashion-service:onnx
docker ps --filter name=fashion --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
curl -s -F "file=@tests/data/pullover.png" localhost:8000/predict/image
sleep 30                                  # 30초 기다렸다가 상태를 다시 본다
docker ps --filter name=fashion --format "table {{.Names}}\t{{.Status}}"
```

```text
e809272f1af563b436d7f6fe191d09022a4d6a56036a803304204bb487328e63
NAMES     IMAGE                  STATUS                            PORTS
fashion   fashion-service:onnx   Up 4 seconds (health: starting)   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
{"file":"pullover.png","label":"풀오버","class_id":2,"probability":0.9998,"top3":[{"label":"풀오버","probability":0.9998},{"label":"T셔츠","probability":0.0001},{"label":"셔츠","probability":0.0}]}
NAMES     STATUS
fashion   Up 34 seconds (healthy)
```

`-d`는 컨테이너를 뒤에서 돌리라는 뜻이고(첫 줄의 긴 글자가 새 컨테이너의 번호입니다), `-p 8000:8000`은 "내 컴퓨터의 8000번 포트로 온 요청을 컨테이너의 8000번 포트로 넘겨라"라는 뜻이에요. 컨테이너는 자기만의 네트워크를 가진 작은 컴퓨터라서, 이렇게 문을 이어 줘야 밖에서 들어갈 수 있습니다. 처음 상태는 `health: starting`이었다가, 30초 뒤에는 첫 헬스 체크를 통과해 `healthy`로 바뀌었습니다. 예측은 맥에서 띄웠을 때와 같은 답이 왔어요. 컨테이너 로그도 볼 수 있습니다.

```bash
docker logs fashion
```

```text
INFO:     Started server process [1]
INFO:     Waiting for application startup.
2026-10-21 07:02:03.082696426 [W:onnxruntime:Default, telemetry_1ds.cc:600 operator()] Failed to persist telemetry device ID; using an in-memory identifier
INFO:     모델 준비 완료: backend=onnx, sha256=265e35c606cf
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     192.168.65.1:34036 - "POST /predict/image HTTP/1.1" 200 OK
INFO:     127.0.0.1:50952 - "GET /health HTTP/1.1" 200 OK
```

모델 지문이 맥에서 띄웠을 때와 같은 `265e35c606cf`입니다. 같은 모델 파일이 상자에 담겨 왔다는 확인이에요. 셋째 줄의 ONNX Runtime 경고는 `USER nobody`로 실행해서 생긴 것입니다. ONNX Runtime이 사용 통계에 쓸 기기 번호를 홈 폴더에 저장하려다 권한이 없어 못 했다는 뜻이라, 서비스에는 영향이 없어요. 마지막 두 줄의 요청 주소도 보세요. 우리가 `curl`로 보낸 예측 요청은 `192.168.65.1`, 즉 컨테이너 밖에서 들어왔고, `/health` 요청은 `127.0.0.1`, 컨테이너 안에서 왔습니다. `HEALTHCHECK`가 30초마다 부른 것이 이 줄이에요.

다 쓴 컨테이너와 이미지는 지워 둡니다. 이미지는 디스크를 꽤 차지하니까요.

```bash
docker rm -f fashion
docker rmi fashion-service:onnx fashion-service:torch-cpu fashion-service:torch
```

`docker rm -f`는 돌고 있는 컨테이너를 멈추고 지우고, `docker rmi`는 이미지를 지웁니다.

> **Q. 이 이미지를 클라우드에 올리려면 어떻게 하나요?**
> 이미지를 **레지스트리**(이미지 저장소)에 `docker push`로 올리고, 서버에서 `docker pull`로 받아 `docker run`하는 것이 기본 흐름입니다. 클라우드 회사들은 저마다 레지스트리와 "이미지를 주면 알아서 띄워 주는" 서비스를 갖추고 있어요. 다만 회사마다 방법이 달라서 이 책에서는 다루지 않습니다. 이 장에서 만든 것처럼 `/health`가 있고, 설정을 환경 변수로 받고, 포트 하나로 HTTP를 받는 이미지라면 어느 곳에 올려도 거의 그대로 돌아가요. 21장 종합 프로젝트도 Docker 이미지까지 만듭니다.

## 20.12 정리와 다음 장 미리보기

이 장에서 학습한 모델을 다른 프로그램이 쓸 수 있는 웹 서비스로 만들었습니다.

- **불러오기**: 서버가 켜질 때 한 번. `lifespan`의 `yield` 앞에서 올려 `app.state`에 둔다. `map_location="cpu"`, `weights_only=True`, `.eval()`. 테스트는 `with TestClient(app)`로 열어야 lifespan이 돈다
- **스키마와 파일**: `Annotated`와 `Field`로 모양·범위 검사, 응답 모델은 자동 문서에. `UploadFile`, 한도보다 1바이트만 더 읽어 크기 검사, 사진이 아니면 400, 너무 크면 413
- **전처리**: 학습 때와 똑같이. 흰 배경 사진을 그대로 넣으면 90.7%가 28.4%로 무너졌다. 서빙할 곳의 실제 입력을 보고 맞추기
- **배치**: 묶을수록 한 장당 빠르다(512장이면 열 배쯤). 여러 장 엔드포인트에는 상한을, 따로 온 요청은 대기 줄과 `Future`로 잠깐 모아 한 번에(동적 배칭)
- **async**: 추론하는 경로 함수는 그냥 `def`로, `async def`라면 추론만 `run_in_threadpool`로. 그래야 계산 중에도 `/health`에 답한다
- **운영 정보**: `/health`(살아 있나), `/ready`(준비됐나), `/version`(모델 파일 해시), 미들웨어로 처리 시간 헤더
- **백엔드 바꾸기**: NumPy 배열을 주고받는 `Protocol` 약속, 환경 변수로 고르기. ONNX Runtime이면 torch 없이
- **지연 시간**: 평균 말고 p50·p95·p99. 작은 모델은 모델보다 HTTP 처리가 비싸다. 재 보고 고칠 곳을 정한다
- **스트리밍**: `StreamingResponse`와 제너레이터, LLM은 `TextIteratorStreamer` + 생성 스레드. 첫 조각까지의 시간이 체감 속도
- **테스트**: pytest 픽스처로 `TestClient` 열기, `dependency_overrides`로 가짜 모델 끼우기, 없는 패키지는 `importorskip`
- **부하와 워커**: 워커 수 × 계산 스레드 수가 코어 수를 넘으면 오히려 느려진다(과다 구독)
- **Docker**: 다단계 빌드로 uv 가상 환경만 옮겨 담기, 의존성 먼저·코드 나중, root가 아닌 사용자, `HEALTHCHECK`, `--host 0.0.0.0`. torch를 빼면 9.22GB가 445MB로

이 장으로 Part 4 실무 편이 끝났습니다. 데이터를 준비하고(Part 1), 모델을 만들고(Part 2, 3), 실험을 관리하고, 가볍게 만들고, 서비스로 내놓는 데까지(Part 4) 한 바퀴를 돌았어요. 다음 21장은 이 책의 마지막 장인 종합 프로젝트입니다. PyTorch 임베딩으로 취향을 배우는 **맛집 추천 AI**를 처음부터 만들고, 이 장에서 익힌 방법 그대로 FastAPI 서비스와 테스트, Docker 이미지까지 완성합니다. 각 장에서 따로 배운 조각들이 하나의 제품으로 맞물리는 모습을 보게 될 거예요.
