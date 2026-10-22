# Chapter 19: 웹 개발 기초

> **학습 목표**  
> - HTTP 요청과 응답이 오가는 원리 이해
> - FastAPI로 웹 API 만들기
> - Pydantic 모델로 요청 데이터 자동 검증하기
> - RESTful API 설계와 상태 코드 활용
> - 웹 보안의 기본 원칙 적용

---

## 들어가며: 웹은 어떻게 대화할까요?

브라우저 주소창에 주소를 치고 엔터를 누르면 화면이 뜨죠. 그 짧은 순간에 무슨 일이 일어난 걸까요?

식당에서 주문하는 장면을 떠올려 보세요.

- 손님은 메뉴판을 보고 **주문서**를 씁니다. "김치찌개 하나, 덜 맵게."
- 종업원이 주문서를 주방에 전합니다.
- 주방은 음식을 만들어 **영수증**과 함께 내보냅니다. 재료가 떨어졌으면 "그 메뉴는 지금 없어요"라고 알려 주죠.

웹도 똑같습니다. 손님이 **클라이언트**(브라우저, 스마트폰 앱, 파이썬 프로그램), 주방이 **서버**, 주문서가 **요청(request)**, 음식이 **응답(response)** 이에요. 그리고 손님과 주방이 같은 양식의 주문서를 쓰자고 정해 둔 약속이 **HTTP**입니다. 주문서 양식이 정해져 있으니 처음 가는 식당에서도 주문할 수 있는 것처럼, HTTP 덕분에 어떤 브라우저든 어떤 서버와도 대화할 수 있습니다.

이 장에서 우리는 주방, 즉 서버 쪽을 만듭니다. 도구는 **FastAPI**예요. 파이썬 웹 프레임워크로는 Flask나 Django도 오래 쓰여 왔지만, FastAPI는 이 책에서 이미 배운 것들을 그대로 씁니다. 2장의 타입 힌트로 "이 값은 정수"라고 적으면 검사가 되고, 8장의 Pydantic 모델로 "주문서 양식"을 정의하면 잘못 쓴 주문서를 알아서 돌려보내고, 15장의 `async`/`await`도 그대로 쓸 수 있습니다. 게다가 메뉴판(API 문서)까지 자동으로 만들어 줍니다.

## 19.1 HTTP 프로토콜의 이해

웹 개발을 시작하기 전에 HTTP(HyperText Transfer Protocol)를 먼저 알아야 합니다. 프레임워크가 많은 일을 대신해 주지만, 결국 우리가 다루는 것은 HTTP 요청과 응답이기 때문이에요.

### 요청과 응답은 이렇게 생겼습니다

HTTP 요청은 사실 그냥 글자입니다. 맛집 목록을 달라는 요청은 대략 이렇게 생겼어요.

```text
GET /restaurants?지역=서울 HTTP/1.1
Host: localhost:8000
Accept: application/json
```

첫 줄이 핵심입니다. **무엇을 할지**(`GET`), **어디에**(`/restaurants`), **어떤 조건으로**(`?지역=서울`)가 들어 있죠. 그 아래 줄들은 **헤더(header)** 라고 부르는 부가 정보입니다. "JSON으로 주세요" 같은 요청 사항을 적는 곳이에요.

서버의 응답도 비슷한 모양입니다.

```text
HTTP/1.1 200 OK
content-type: application/json

{"개수": 1, "결과": ["명동교자"]}
```

첫 줄의 `200 OK`가 **상태 코드**, 그 아래가 헤더, 빈 줄 다음이 **본문(body)** 입니다. 영수증 맨 위에 "주문 완료"라고 찍혀 있고 그 아래에 음식이 나오는 셈이죠.

### HTTP 메서드: 무엇을 할지 정하는 동사

요청 첫 줄의 `GET` 자리에 오는 단어를 **메서드(method)** 라고 합니다. 같은 주소라도 메서드에 따라 하는 일이 달라져요. 실무에서 자주 쓰는 다섯 가지는 다음과 같습니다.

| 메서드 | 하는 일 | 맛집 서비스 예 |
|---|---|---|
| `GET` | 데이터 조회 | 맛집 목록 가져오기 |
| `POST` | 새 데이터 생성 | 새 리뷰 작성 |
| `PUT` | 데이터 전체 교체 | 맛집 정보를 통째로 수정 |
| `PATCH` | 데이터 일부 수정 | 평점만 수정 |
| `DELETE` | 데이터 삭제 | 리뷰 삭제 |

`GET`은 "보기만" 하는 요청이라 몇 번을 보내도 서버의 데이터가 바뀌지 않아야 합니다. 새로고침을 열 번 눌렀다고 리뷰가 열 개 생기면 곤란하겠죠? 그래서 데이터를 만들거나 바꾸는 일은 `POST`, `PUT`, `PATCH`, `DELETE`에 맡깁니다.

### HTTP 상태 코드: 결과를 알려 주는 숫자

응답 첫 줄의 숫자는 요청이 어떻게 됐는지 알려 줍니다. 백 단위로 뜻이 나뉘어요.

- **2xx 성공**: 주문대로 나왔습니다.
- **4xx 클라이언트 오류**: 손님이 주문서를 잘못 썼거나, 없는 메뉴를 시켰습니다.
- **5xx 서버 오류**: 주방에 문제가 생겼습니다.

파이썬 표준 라이브러리의 `http.HTTPStatus`에 모든 상태 코드가 이름과 함께 들어 있습니다. 이 장에서 자주 만날 코드들을 확인해 볼게요.

```python
from http import HTTPStatus

# 이 장에서 자주 만날 상태 코드
for code in (200, 201, 204, 400, 401, 404, 422, 500):
    status = HTTPStatus(code)
    print(code, status.phrase)

print(HTTPStatus.NOT_FOUND == 404)
```

```text
200 OK
201 Created
204 No Content
400 Bad Request
401 Unauthorized
404 Not Found
422 Unprocessable Entity
500 Internal Server Error
True
```

`201 Created`는 "새로 만들었어요", `204 No Content`는 "처리했는데 돌려줄 내용은 없어요"라는 뜻입니다. 삭제처럼 결과물이 없는 요청에 어울리죠. `422`는 이 장에서 아주 자주 보게 될 코드예요. "주문서 양식은 맞는데 내용이 이상하다", 예를 들어 평점 칸에 7점을 적은 경우입니다. 위 출력은 파이썬 3.12 기준이고, 3.13부터는 422의 이름이 `Unprocessable Content`로 바뀌어 출력됩니다. 숫자는 같아요.

마지막 줄을 보세요. `HTTPStatus.NOT_FOUND == 404`가 `True`입니다. `HTTPStatus`는 정수처럼 비교할 수 있어서, 코드에 `404`라고 숫자를 쓰는 대신 이름으로 써서 뜻을 드러낼 수 있습니다.

---

## 19.2 FastAPI 프레임워크 기초

이제 주방을 차려 봅시다. 웹 서버를 처음부터 만들려면 들어온 글자를 쪼개 메서드와 주소를 알아내고, 응답 글자를 규칙대로 조립하는 일을 모두 직접 해야 합니다. **웹 프레임워크**는 이런 반복 작업을 대신해 주고, 우리는 "이 주소로 요청이 오면 이 함수를 실행해"만 적으면 되게 해 줍니다.

### FastAPI 설치

이 책은 `pip` 대신 `uv`를 씁니다. FastAPI는 기본 패키지만으로도 동작하지만, 개발 서버 실행 명령과 테스트 도구까지 함께 받으려면 `standard` 묶음으로 설치하세요.

```bash
uv add "fastapi[standard]"
```

`[standard]`를 붙이면 개발 서버 `uvicorn`, `fastapi` 명령, 그리고 뒤에서 쓸 테스트 클라이언트가 의존하는 HTTP 라이브러리가 함께 설치됩니다. 이 장의 예제는 FastAPI 0.156.3, Pydantic 2.11.7에서 확인했습니다.

### 첫 번째 FastAPI 애플리케이션

`main.py` 파일을 만들고 다음 코드를 적어 보세요.

```python
# main.py - 첫 번째 FastAPI 애플리케이션
from fastapi import FastAPI

app = FastAPI(title="한국 도시 정보 API")

# 한국 도시 데이터 (실제로는 데이터베이스에서 가져올 것)
한국_도시들 = [
    {"id": 1, "이름": "서울", "지역": "수도권"},
    {"id": 2, "이름": "부산", "지역": "영남권"},
    {"id": 3, "이름": "인천", "지역": "수도권"},
    {"id": 4, "이름": "대구", "지역": "영남권"},
]


@app.get("/")
def 홈():
    return {"메시지": "한국 도시 정보 API에 오신 것을 환영합니다"}


@app.get("/cities")
async def 도시_목록():
    return {"데이터": 한국_도시들, "총개수": len(한국_도시들)}
```

코드가 짧죠? 하나씩 볼게요.

- `app = FastAPI(...)`가 우리 주방입니다. 들어오는 모든 요청이 이 객체를 거칩니다.
- `@app.get("/")`는 10장에서 배운 **데코레이터**예요. "`GET` 메서드로 `/` 주소에 요청이 오면 아래 함수를 실행해"라고 등록하는 겁니다. 이렇게 주소와 함수를 짝지어 주는 것을 **라우팅(routing)**, 등록된 함수를 **경로 함수**라고 부릅니다.
- 함수가 딕셔너리를 돌려주면 FastAPI가 알아서 JSON으로 바꿔 응답 본문에 넣습니다. 우리는 `json.dumps()`를 부를 필요가 없어요.

두 번째 함수는 `async def`로 썼습니다. 15장에서 배운 비동기 함수죠. FastAPI는 둘 다 받아 줍니다. 차이는 실행되는 곳이에요. 일반 `def` 경로 함수는 FastAPI가 따로 마련한 작업 스레드에서 실행하고, `async def` 경로 함수는 이벤트 루프에서 직접 실행합니다. 그래서 함수 안에서 `await`로 기다릴 일(비동기 HTTP 요청, 비동기 DB 드라이버)이 있으면 `async def`를, 그렇지 않거나 `sqlite3`처럼 기다리는 동안 멈추는 라이브러리를 쓴다면 그냥 `def`를 쓰면 됩니다. `async def` 안에서 `time.sleep()`처럼 멈추는 코드를 부르면 이벤트 루프 전체가 멈춰서 다른 손님의 주문까지 밀린다는 점만 기억하세요.

### 실행 방법

개발 중에는 `fastapi dev` 명령으로 서버를 띄웁니다.

```bash
uv run fastapi dev main.py
```

이 명령은 `127.0.0.1`의 `8000`번 포트에서 서버를 띄우고, 파일을 고칠 때마다 서버를 자동으로 다시 시작합니다. 브라우저에서 `http://127.0.0.1:8000/cities`를 열면 JSON이 보일 거예요. 같은 일을 `uvicorn`으로 직접 할 수도 있습니다. `main:app`은 "`main.py` 파일 안의 `app` 객체"라는 뜻이에요.

```bash
uv run uvicorn main:app --reload
```

### 서버 없이 확인하기: TestClient

서버를 띄우고 브라우저를 여는 것도 좋지만, 확인할 때마다 그러기는 번거롭습니다. FastAPI는 **TestClient**라는 가짜 손님을 제공합니다. 서버를 띄우지 않고도 `app`에 진짜와 똑같은 HTTP 요청을 보내고 응답을 받아 볼 수 있어요. 이 장의 모든 결과는 이 방법으로 확인한 것입니다. `main.py`와 같은 폴더에 다음 파일을 만들어 `uv run python try_main.py`로 실행해 보세요.

```python
# try_main.py - 서버를 띄우지 않고 main.py의 API 호출하기
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

응답 = client.get("/")
print(응답.status_code, 응답.json())
print(응답.headers["content-type"])

응답 = client.get("/cities")
print(응답.json()["총개수"], 응답.json()["데이터"][0])

응답 = client.get("/없는-주소")
print(응답.status_code, 응답.json())
```

```text
200 {'메시지': '한국 도시 정보 API에 오신 것을 환영합니다'}
application/json
4 {'id': 1, '이름': '서울', '지역': '수도권'}
404 {'detail': 'Not Found'}
```

딕셔너리를 돌려줬을 뿐인데 상태 코드는 `200`, 헤더의 `content-type`은 `application/json`으로 채워져 있습니다. 등록하지 않은 주소로 요청하면 FastAPI가 알아서 `404`와 `{"detail": "Not Found"}`를 돌려주고요. HTTP 규칙을 지키는 일은 프레임워크가 맡고, 우리는 "무엇을 돌려줄지"만 생각하면 됩니다.

---

## 19.3 라우팅과 경로·쿼리 매개변수

맛집이 천 개라면 경로 함수도 천 개를 만들어야 할까요? 물론 아니죠. 주소의 일부를 **변수**처럼 받으면 됩니다. 값을 받는 자리는 두 군데예요.

- **경로 매개변수**: `/restaurants/3`처럼 주소 자체에 들어가는 값. "3번 맛집"처럼 **무엇을** 가리킬 때 씁니다.
- **쿼리 매개변수**: `/restaurants?지역=서울`처럼 `?` 뒤에 붙는 값. "서울에 있는 것만"처럼 **어떤 조건으로** 고를지 정할 때 씁니다.

### 경로 매개변수와 쿼리 매개변수

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

맛집들 = {
    1: {"이름": "명동교자", "지역": "서울", "종류": "한식", "평점": 4.5},
    2: {"이름": "해운대 암소갈비", "지역": "부산", "종류": "한식", "평점": 4.7},
    3: {"이름": "성심당", "지역": "대전", "종류": "빵집", "평점": 4.8},
}


# 경로 매개변수: 주소의 일부가 곧 값이 된다
@app.get("/restaurants/{restaurant_id}")
def 맛집_상세(restaurant_id: int):
    return 맛집들.get(restaurant_id, {"오류": "없는 맛집입니다"})


# 쿼리 매개변수: 함수 인자 중 경로에 없는 것은 ?뒤에서 찾는다
@app.get("/restaurants")
def 맛집_검색(지역: str | None = None, 최소_평점: float = 0.0):
    결과 = [
        맛집 for 맛집 in 맛집들.values()
        if (지역 is None or 맛집["지역"] == 지역) and 맛집["평점"] >= 최소_평점
    ]
    return {"개수": len(결과), "결과": [맛집["이름"] for 맛집 in 결과]}


client = TestClient(app)
print(client.get("/restaurants/3").json())

응답 = client.get("/restaurants/99")
print(응답.status_code, 응답.json())
print(client.get("/restaurants", params={"최소_평점": 4.6}).json())
print(client.get("/restaurants?지역=서울").json())

응답 = client.get("/restaurants/세번째")
print(응답.status_code)
print(응답.json())
```

```text
{'이름': '성심당', '지역': '대전', '종류': '빵집', '평점': 4.8}
200 {'오류': '없는 맛집입니다'}
{'개수': 2, '결과': ['해운대 암소갈비', '성심당']}
{'개수': 1, '결과': ['명동교자']}
422
{'detail': [{'type': 'int_parsing', 'loc': ['path', 'restaurant_id'], 'msg': 'Input should be a valid integer, unable to parse string as an integer', 'input': '세번째'}]}
```

규칙은 간단합니다. 주소 문자열의 `{restaurant_id}`와 이름이 같은 함수 인자는 경로에서 값을 받고, 나머지 인자는 쿼리 매개변수가 됩니다. 기본값이 있는 쿼리 매개변수(`지역=None`, `최소_평점=0.0`)는 생략해도 되고요. `params=` 인자로 딕셔너리를 넘기든 주소에 `?지역=서울`을 직접 쓰든 결과는 같습니다.

출력에서 꼭 볼 곳이 세 군데 있습니다.

첫째, 주소로 들어온 값은 원래 전부 **문자열**입니다. `/restaurants/3`의 `3`도 글자 "3"이죠. 그런데 `맛집들.get(restaurant_id)`가 정수 키 `3`을 찾아냈습니다. `restaurant_id: int`라는 타입 힌트를 보고 FastAPI가 정수로 바꿔 넘겨줬기 때문이에요. `최소_평점`도 `float`로 바뀌어 `>=` 비교가 됐습니다.

둘째, `/restaurants/세번째`처럼 정수로 바꿀 수 없는 값이 오면 경로 함수는 아예 실행되지 않고 `422`가 돌아옵니다. `detail` 안의 `loc`가 `['path', 'restaurant_id']`, 즉 "경로의 restaurant_id 자리가 문제"라고 정확히 짚어 주죠. 타입 힌트 한 줄이 입력 검사 코드 여러 줄을 대신한 셈입니다.

셋째, 없는 맛집 `99`번을 요청했는데 상태 코드가 `200`입니다. 본문에는 "없는 맛집"이라고 써 놓고 영수증에는 "주문 완료"라고 찍은 꼴이죠. 이 문제는 19.6절에서 `HTTPException`으로 바로잡습니다.

> **Q. 경로 매개변수 이름을 `{맛집_id}`처럼 한글로 쓰면 안 되나요?**  
> 안 됩니다. 실제로 `@app.get("/restaurants/{맛집_id}")`로 바꿔 실행해 보면 `/restaurants/3` 요청이 오류 없이 `404 Not Found`가 됩니다. FastAPI가 쓰는 라우팅 엔진(Starlette)은 `{}` 안의 이름으로 영문자·숫자·밑줄만 알아보기 때문에, 한글 이름이 든 주소는 `{맛집_id}`라는 글자 그대로의 주소로 취급돼요. 오류 메시지 없이 조용히 404가 나니 찾기 어려운 실수입니다. 경로 매개변수 이름은 영어로 쓰세요. 쿼리 매개변수 이름(`지역`, `최소_평점`)이나 경로에 들어오는 **값**(`/search/서울`)은 한글이어도 괜찮습니다.

---

## 19.4 의존성 주입과 자동 API 문서

식당 주방을 떠올려 보세요. 요리사마다 칼을 갈고, 도마를 씻고, 냉장고 문을 여는 일을 매번 따로 하지는 않습니다. 공용 준비는 한곳에서 해 두고, 요리사는 "칼 주세요"라고 하면 받아 쓰죠.

API도 마찬가지입니다. 페이지 나누기, 데이터베이스 연결, 로그인 확인처럼 여러 경로 함수가 똑같이 필요로 하는 준비 작업이 있어요. 이것을 함수마다 복사해 넣는 대신, 준비 함수를 하나 만들어 두고 경로 함수가 "이거 필요해요"라고 선언하면 FastAPI가 실행해서 결과를 넣어 줍니다. 이것을 **의존성 주입(dependency injection)** 이라고 하고, 선언할 때는 `Depends`를 씁니다.

### Depends로 공통 준비 작업 나누기

```python
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

app = FastAPI(title="맛집 API", version="1.0.0")

맛집_이름들 = [f"맛집_{번호}" for 번호 in range(1, 26)]


# 여러 경로가 함께 쓰는 '페이지 나누기' 규칙
def 페이지_정보(page: int = 1, size: int = 10) -> dict:
    return {"시작": (page - 1) * size, "끝": page * size, "page": page}


# 요청마다 자원을 열고, 응답이 끝나면 닫는 의존성
def 저장소_연결():
    print("  [저장소 열기]")
    yield 맛집_이름들
    print("  [저장소 닫기]")


@app.get("/restaurants")
def 맛집_목록(
    페이지: dict = Depends(페이지_정보),
    저장소: list = Depends(저장소_연결),
):
    print("  [경로 함수 실행]")
    return {"page": 페이지["page"], "결과": 저장소[페이지["시작"]:페이지["끝"]]}


client = TestClient(app)
print(client.get("/restaurants", params={"page": 3, "size": 4}).json())
```

```text
  [저장소 열기]
  [경로 함수 실행]
  [저장소 닫기]
{'page': 3, '결과': ['맛집_9', '맛집_10', '맛집_11', '맛집_12']}
```

`페이지_정보`는 평범한 함수인데, 그 인자 `page`와 `size`가 쿼리 매개변수가 됐습니다. 의존성 함수의 매개변수도 경로 함수의 매개변수처럼 요청에서 값을 받기 때문이에요. 이제 페이지 나누기가 필요한 경로 함수마다 `Depends(페이지_정보)` 한 줄만 쓰면 됩니다. 규칙을 바꿀 때도 이 함수 하나만 고치면 되고요.

`저장소_연결`은 `return` 대신 `yield`를 썼습니다. 15장의 제너레이터 문법이죠. 출력 순서를 보면 `yield` 앞부분(열기)이 경로 함수보다 먼저, `yield` 뒷부분(닫기)이 경로 함수가 끝난 뒤에 실행됐습니다. 12장의 `with` 문처럼 "빌리고, 쓰고, 반드시 돌려주기"를 요청 단위로 해 주는 셈이에요. 실습 프로젝트에서 데이터베이스 연결을 이 방식으로 관리합니다.

### 자동 API 문서: /docs와 /openapi.json

식당에 메뉴판이 없으면 손님은 뭘 시켜야 할지 모릅니다. API도 "어떤 주소에 어떤 값을 보내면 무엇이 돌아오는지" 적은 문서가 필요해요. 그런데 문서를 따로 쓰면 코드를 고칠 때마다 문서도 고쳐야 하고, 대개 그러다 어긋나죠.

FastAPI는 우리가 쓴 경로 함수와 타입 힌트를 읽어서 메뉴판을 자동으로 만듭니다. 바로 위 예제 아래에 이어 붙여 실행해 보세요.

```python
스키마 = client.get("/openapi.json").json()
print(스키마["openapi"], 스키마["info"])
for 경로, 메서드들 in 스키마["paths"].items():
    for 메서드, 정보 in 메서드들.items():
        이름들 = [매개변수["name"] for 매개변수 in 정보["parameters"]]
        print(메서드.upper(), 경로, 정보["summary"], 이름들)

화면 = client.get("/docs")
print(화면.status_code, 화면.headers["content-type"])
```

```text
3.1.0 {'title': '맛집 API', 'version': '1.0.0'}
GET /restaurants 맛집 목록 ['page', 'size']
200 text/html; charset=utf-8
```

`/openapi.json`은 우리가 만든 적 없는 주소인데 응답이 옵니다. **OpenAPI**라는 표준 형식(여기서는 3.1.0판)으로 작성된 API 명세서예요. `FastAPI(title=..., version=...)`에 넣은 값이 `info`에 들어 있고, `GET /restaurants`의 요약(`summary`)은 함수 이름 `맛집_목록`에서 밑줄을 공백으로 바꿔 만든 것입니다. 매개변수 목록에 `page`와 `size`가 보이죠? 경로 함수에는 없고 의존성 함수에 있던 매개변수까지 찾아서 적어 준 거예요. 이 명세에는 각 매개변수가 쿼리에 들어간다는 것, 타입이 정수이고 기본값이 1과 10이라는 것, 성공하면 200, 값이 잘못되면 422가 돌아온다는 것까지 기록되어 있습니다.

`/docs`는 이 명세를 사람이 보기 좋게 보여 주는 **Swagger UI** 화면입니다. 응답이 HTML이고, 실제로 받은 페이지를 열어 보면 `/openapi.json`을 읽어 화면을 그리도록 되어 있습니다. 서버를 띄운 뒤 브라우저로 `http://127.0.0.1:8000/docs`에 들어가면 경로마다 매개변수를 입력하고 직접 요청을 보내 볼 수 있어요. 이 화면을 그리는 자바스크립트와 스타일은 인터넷(CDN)에서 받아 오므로, 오프라인에서는 화면이 비어 보일 수 있습니다. 같은 명세를 다른 모양으로 보여 주는 `/redoc` 화면도 함께 제공됩니다.

메뉴판이 코드에서 만들어지니 코드와 문서가 어긋날 일이 없습니다. 함수에 매개변수를 하나 추가하면 문서에도 바로 나타나요.

---

## 19.5 요청 본문 검증: Pydantic 모델

리뷰를 작성할 때는 작성자, 평점, 내용처럼 보낼 값이 많습니다. 이런 값을 모두 주소에 붙이면 너무 길어지고, 주소는 기록에도 남으니 적절하지 않죠. 그래서 `POST`나 `PUT` 요청은 데이터를 **본문(body)** 에 JSON으로 담아 보냅니다.

본문으로 무엇이든 보낼 수 있다는 것은 무엇이든 잘못 올 수 있다는 뜻이기도 합니다. 평점에 7점, 작성자 이름에 한 글자, 내용 없이 빈 리뷰… 이걸 `if` 문으로 하나하나 검사하면 경로 함수의 절반이 검사 코드가 됩니다.

8장에서 배운 Pydantic이 여기서 빛을 발합니다. **주문서 양식**을 Pydantic 모델로 정의하고 경로 함수의 인자 타입으로 쓰면, FastAPI가 본문 JSON을 그 모델에 맞춰 검사하고 변환해서 넘겨줍니다.

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

app = FastAPI()


class ReviewCreate(BaseModel):
    작성자: str = Field(min_length=2, max_length=10)
    평점: int = Field(ge=1, le=5)
    내용: str = Field(min_length=10)
    재방문: bool = False


리뷰들: list[dict] = []


@app.post("/restaurants/{restaurant_id}/reviews", status_code=201)
def 리뷰_작성(restaurant_id: int, 리뷰: ReviewCreate):
    저장할_리뷰 = {
        "id": len(리뷰들) + 1,
        "restaurant_id": restaurant_id,
        **리뷰.model_dump(),
    }
    리뷰들.append(저장할_리뷰)
    return 저장할_리뷰


client = TestClient(app)

응답 = client.post(
    "/restaurants/3/reviews",
    json={"작성자": "김철수", "평점": "5", "내용": "튀김소보로가 정말 맛있어요!"},
)
print(응답.status_code, 응답.json())

응답 = client.post(
    "/restaurants/3/reviews",
    json={"작성자": "김", "평점": 7, "내용": "맛있어요"},
)
print(응답.status_code)
for 오류 in 응답.json()["detail"]:
    print(오류["loc"], 오류["msg"])
```

```text
201 {'id': 1, 'restaurant_id': 3, '작성자': '김철수', '평점': 5, '내용': '튀김소보로가 정말 맛있어요!', '재방문': False}
422
['body', '작성자'] String should have at least 2 characters
['body', '평점'] Input should be less than or equal to 5
['body', '내용'] String should have at least 10 characters
```

경로 함수 `리뷰_작성` 안에는 검사 코드가 한 줄도 없습니다. 그런데도 결과를 보면,

- 첫 요청은 평점을 문자열 `"5"`로 보냈는데 응답에는 정수 `5`로 들어 있습니다. 8장에서 본 Pydantic의 자동 타입 변환이죠. 보내지 않은 `재방문`은 기본값 `False`가 채워졌고요. `status_code=201`로 정해 둔 대로 "새로 만들었어요"가 돌아왔습니다.
- 두 번째 요청은 경로 함수까지 가지도 못하고 `422`로 돌아왔습니다. 그리고 틀린 곳을 **한꺼번에** 알려 줍니다. 하나 고치고 다시 보냈더니 또 다른 데가 틀렸다고 하는 일이 없어요. `loc`의 첫 값 `'body'`는 "본문에서", 둘째 값은 "어느 필드에서"를 뜻합니다.

함수가 어떤 매개변수를 어디서 받는지는 타입이 정합니다. `restaurant_id: int`처럼 기본 타입이면 경로나 쿼리에서, `리뷰: ReviewCreate`처럼 Pydantic 모델이면 본문에서 받아요.

> **Q. 필드 이름은 한글인데 왜 클래스 이름은 `ReviewCreate`처럼 영어로 썼나요?**  
> 자동 문서 때문입니다. FastAPI는 모델 클래스 이름을 OpenAPI 명세의 스키마 이름으로 쓰는데, 이 이름에 쓸 수 없는 글자는 밑줄로 바꿉니다. 실제로 모델 이름을 `상품입력`, `상품`으로 지어 `/openapi.json`을 열어 보면 스키마 이름이 `__`와 `____`가 되어 버려요. 글자 수만 남으니 같은 길이의 한글 이름 두 개는 구별할 수도 없습니다. 모델 클래스 이름은 영어로 짓고, 필드 이름은 한글로 써도 명세에 그대로 나옵니다. 다만 다른 프로그램(웹 프런트엔드, 모바일 앱)과 주고받는 JSON이라면 필드 이름도 영어로 맞추는 경우가 많습니다. 실습 프로젝트는 그렇게 만들었어요.

---

## 19.6 RESTful API 설계와 구현

지금까지 주소를 그때그때 지었습니다. 그런데 주소를 짓는 사람마다 `/getProducts`, `/product_list`, `/deleteProduct?id=1`처럼 제각각이면, API를 쓰는 사람은 주소를 전부 외워야 하죠.

**REST**는 이 혼란을 줄이는 설계 방식입니다. 핵심은 두 가지예요.

1. 주소는 **명사**로, 다루는 대상(자원)을 가리킨다: `/api/products`(상품 전체), `/api/products/1`(1번 상품)
2. 할 일은 **HTTP 메서드**라는 동사로 정한다: 같은 `/api/products/1`이라도 `GET`이면 조회, `PUT`이면 수정, `DELETE`면 삭제

이 규칙을 따르면 데이터를 만들고(Create), 읽고(Read), 고치고(Update), 지우는(Delete) 네 가지 기본 동작, 줄여서 **CRUD**가 다음처럼 정리됩니다.

| 동작 | 메서드와 주소 | 성공 상태 코드 |
|---|---|---|
| 목록 조회 | `GET /api/products` | 200 |
| 등록 | `POST /api/products` | 201 |
| 하나 조회 | `GET /api/products/{product_id}` | 200 |
| 전체 수정 | `PUT /api/products/{product_id}` | 200 |
| 삭제 | `DELETE /api/products/{product_id}` | 204 |

### 한국 쇼핑몰 상품 API

이 표를 그대로 코드로 옮겨 봅시다. 19.3절에서 남겨 둔 숙제, "없는 상품인데 200이 나가는 문제"도 함께 해결합니다. 다음 코드를 `crud.py`로 저장하세요.

```python
# crud.py - 상품 CRUD API
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="한국 쇼핑몰 API")


class ProductIn(BaseModel):
    이름: str = Field(min_length=1, max_length=50)
    가격: int = Field(gt=0)
    재고: int = Field(default=0, ge=0)


class Product(ProductIn):
    id: int


상품_저장소: dict[int, Product] = {}
다음_id = 1


def 상품_찾기(product_id: int) -> Product:
    if product_id not in 상품_저장소:
        raise HTTPException(status_code=404, detail=f"{product_id}번 상품이 없습니다")
    return 상품_저장소[product_id]


@app.get("/api/products")
def 상품_목록() -> list[Product]:
    return list(상품_저장소.values())


@app.post("/api/products", status_code=status.HTTP_201_CREATED)
def 상품_등록(입력: ProductIn) -> Product:
    global 다음_id
    새_상품 = Product(id=다음_id, **입력.model_dump())
    상품_저장소[다음_id] = 새_상품
    다음_id += 1
    return 새_상품


@app.get("/api/products/{product_id}")
def 상품_조회(product_id: int) -> Product:
    return 상품_찾기(product_id)


@app.put("/api/products/{product_id}")
def 상품_수정(product_id: int, 입력: ProductIn) -> Product:
    상품_찾기(product_id)
    수정된_상품 = Product(id=product_id, **입력.model_dump())
    상품_저장소[product_id] = 수정된_상품
    return 수정된_상품


@app.delete("/api/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def 상품_삭제(product_id: int) -> None:
    상품_찾기(product_id)
    del 상품_저장소[product_id]
```

눈여겨볼 점이 세 가지 있습니다.

**입력 모델과 출력 모델을 나눴습니다.** 상품을 등록할 때 클라이언트가 `id`를 정하면 안 되죠. 번호는 서버가 매깁니다. 그래서 클라이언트가 보내는 `ProductIn`에는 `id`가 없고, 서버가 돌려주는 `Product`는 `ProductIn`을 상속(13장)해 `id`만 더했습니다.

**반환 타입 힌트가 응답 모델이 됩니다.** `-> Product`라고 적으면 FastAPI는 돌려줄 값을 `Product` 모양으로 검사·정리해서 내보내고, 자동 문서에도 "성공하면 이런 모양이 돌아온다"고 적습니다.

**오류는 `HTTPException`으로 던집니다.** 12장에서 배운 `raise`를 그대로 쓰는 거예요. 경로 함수 깊은 곳(여기서는 `상품_찾기`)에서 예외를 던지면 FastAPI가 받아서 지정한 상태 코드와 `{"detail": ...}` 본문으로 응답합니다. 덕분에 조회·수정·삭제 세 함수가 "없으면 404"를 한 줄로 해결했어요.

상태 코드는 `201` 대신 `status.HTTP_201_CREATED`처럼 이름으로 쓸 수도 있습니다. 숫자를 외우지 않아도 뜻이 읽히죠.

### API 확인하기

이제 손님 역할을 해 봅시다. 요청을 보내고 결과를 한 줄로 찍는 작은 함수를 만들어 차례로 호출합니다.

```python
# crud_try.py
from fastapi.testclient import TestClient

from crud import app

client = TestClient(app)


def 요청(메서드: str, 주소: str, **옵션) -> None:
    응답 = client.request(메서드, 주소, **옵션)
    본문 = 응답.json() if 응답.content else "(본문 없음)"
    print(f"{메서드:6} {주소:18} -> {응답.status_code} {본문}")


요청("POST", "/api/products", json={"이름": "무선 이어폰", "가격": 89000, "재고": 30})
요청("POST", "/api/products", json={"이름": "보조배터리", "가격": 25000})
요청("GET", "/api/products")
요청("PUT", "/api/products/2", json={"이름": "보조배터리", "가격": 23000, "재고": 5})
요청("DELETE", "/api/products/1")
요청("GET", "/api/products/1")
요청("DELETE", "/api/products/1")
```

```text
POST   /api/products      -> 201 {'이름': '무선 이어폰', '가격': 89000, '재고': 30, 'id': 1}
POST   /api/products      -> 201 {'이름': '보조배터리', '가격': 25000, '재고': 0, 'id': 2}
GET    /api/products      -> 200 [{'이름': '무선 이어폰', '가격': 89000, '재고': 30, 'id': 1}, {'이름': '보조배터리', '가격': 25000, '재고': 0, 'id': 2}]
PUT    /api/products/2    -> 200 {'이름': '보조배터리', '가격': 23000, '재고': 5, 'id': 2}
DELETE /api/products/1    -> 204 (본문 없음)
GET    /api/products/1    -> 404 {'detail': '1번 상품이 없습니다'}
DELETE /api/products/1    -> 404 {'detail': '1번 상품이 없습니다'}
```

등록은 `201`, 삭제는 본문 없는 `204`, 지워진 상품을 다시 찾으면 `404`. 상태 코드만 봐도 무슨 일이 있었는지 알 수 있습니다. 이게 REST 설계의 힘이에요. API를 쓰는 쪽은 본문을 뒤지지 않고도 `if 응답.status_code == 404:`처럼 결과를 판단할 수 있습니다.

> **Q. `PUT`과 `PATCH`는 어떻게 구분하나요?**  
> `PUT`은 **통째로 교체**입니다. 위 예에서 2번 상품을 `PUT`할 때 이름·가격·재고를 모두 보낸 이유예요. `재고`를 빼고 보내면 기본값 0으로 바뀌어 버립니다. 가격 하나만 바꾸고 싶다면 보낸 필드만 고치는 `PATCH`가 어울립니다. 실습 프로젝트의 글 수정 기능을 `PATCH`로 만들었으니 비교해 보세요.

---

## 19.7 보안 기본

식당이 문을 열면 좋은 손님만 오지는 않습니다. 웹 서버는 인터넷의 누구든 요청을 보낼 수 있는 곳이에요. 처음부터 지켜야 할 기본기 네 가지를 봅시다.

### 1. 입력은 믿지 않는다

19.5절에서 본 것처럼 Pydantic 모델과 `Field` 제약으로 들어오는 값의 타입·길이·범위를 정해 두는 것이 첫 번째 방어선입니다. 검사를 통과한 값만 경로 함수에 들어오니까요.

그 값을 데이터베이스에 넣을 때는 18장에서 배운 대로 **반드시 `?` 자리표시자**를 씁니다. `f"SELECT * FROM posts WHERE title = '{제목}'"`처럼 문자열을 이어 붙이면, 제목 칸에 SQL 조각을 적어 보내는 것만으로 쿼리 전체가 바뀌는 **SQL 인젝션** 공격에 뚫립니다. 자리표시자를 쓰면 값은 언제나 "값"으로만 취급됩니다.

또 하나, FastAPI는 딕셔너리를 JSON으로 돌려주므로 사용자가 쓴 글에 `<script>`가 들어 있어도 그냥 문자열로 전달됩니다. 하지만 HTML을 직접 조립해서 돌려줄 때는 사용자 입력을 `html.escape()`로 바꿔 넣어야 다른 사용자의 브라우저에서 스크립트가 실행되는 공격(XSS)을 막을 수 있어요.

### 2. 비밀번호는 저장하지 않는다

회원 비밀번호를 그대로 데이터베이스에 넣으면, 데이터베이스가 한 번 유출되는 순간 모든 회원의 비밀번호가 드러납니다. 그래서 비밀번호 대신 **해시(hash)** 를 저장합니다. 해시는 한쪽 방향으로만 계산되는 지문 같은 값이에요. 비밀번호로 해시를 만들기는 쉽지만, 해시로 비밀번호를 되돌리기는 사실상 불가능합니다. 로그인할 때는 입력한 비밀번호로 다시 해시를 만들어 저장된 해시와 비교하면 되죠.

별도 패키지 없이 표준 라이브러리의 `hashlib.pbkdf2_hmac`으로 만들 수 있습니다.

```python
import hashlib
import hmac
import secrets

반복_횟수 = 600_000  # 반복할수록 무차별 대입이 느려진다


def 비밀번호_해시(비밀번호: str) -> str:
    소금 = secrets.token_bytes(16)  # 사용자마다 다른 무작위 값
    해시 = hashlib.pbkdf2_hmac("sha256", 비밀번호.encode(), 소금, 반복_횟수)
    return f"{소금.hex()}${해시.hex()}"


def 비밀번호_확인(비밀번호: str, 저장된_값: str) -> bool:
    소금_hex, 해시_hex = 저장된_값.split("$")
    소금 = bytes.fromhex(소금_hex)
    해시 = hashlib.pbkdf2_hmac("sha256", 비밀번호.encode(), 소금, 반복_횟수)
    return hmac.compare_digest(해시.hex(), 해시_hex)


저장값_1 = 비밀번호_해시("서울2025!")
저장값_2 = 비밀번호_해시("서울2025!")
print(len(저장값_1), 저장값_1 == 저장값_2)
print(비밀번호_확인("서울2025!", 저장값_1))
print(비밀번호_확인("부산2025!", 저장값_1))
```

```text
97 False
True
False
```

첫 줄의 `False`가 중요합니다. 같은 비밀번호로 두 번 해시를 만들었는데 결과가 다르죠? **소금(salt)** 이라고 부르는 무작위 값을 섞었기 때문이에요. 소금이 없으면 같은 비밀번호를 쓰는 회원들의 해시가 똑같아져서, 흔한 비밀번호의 해시를 미리 계산해 둔 표로 한꺼번에 알아낼 수 있습니다. 소금은 비밀이 아니라서 해시 옆에 함께 저장하고(`소금$해시`, 32 + 1 + 64 = 97글자), 확인할 때 꺼내 씁니다.

`반복_횟수`는 해시 계산을 일부러 수십만 번 반복하게 해서, 공격자가 비밀번호를 하나씩 대입해 보는 속도를 늦춥니다. 로그인 한 번에 수십만 번은 티가 안 나지만, 수억 개를 대입하려는 공격자에게는 큰 벽이 되죠.

마지막으로 비교할 때 `==` 대신 `hmac.compare_digest()`를 썼습니다. `==`는 앞 글자부터 비교하다 다른 글자를 만나면 바로 멈추기 때문에, 응답 시간을 재면 몇 글자까지 맞았는지 힌트가 새어 나갈 수 있어요. `compare_digest`는 어디서 달라지든 같은 방식으로 끝까지 비교합니다.

### 3. 비밀 값은 코드 밖에 둔다

API 키, 데이터베이스 비밀번호 같은 값을 코드에 적어 두면 코드를 공유하는 순간 함께 퍼집니다. 이런 값은 **환경 변수**에서 읽으세요. 17장에서 본 `os.environ`을 쓰면 됩니다. 아래 예제의 `os.environ.get("BLOG_API_KEY", "dev-only-key")`는 환경 변수가 있으면 그 값을, 없으면 개발용 기본값을 씁니다. 실제 서비스에서는 기본값 없이 `os.environ["BLOG_API_KEY"]`로 읽어서, 설정을 빠뜨리면 아예 시작하지 않게 하는 편이 안전합니다.

### 4. 누가 무엇을 할 수 있는지 정한다: 인증과 CORS

글 목록은 누구나 봐도 되지만, 글쓰기는 관리자만 해야겠죠. 19.4절의 의존성이 여기서 다시 쓰입니다. "API 키를 확인하는 의존성"을 만들어 글쓰기 경로에만 붙이면 됩니다.

또 하나, 브라우저는 보안을 위해 **다른 출처**(도메인·포트가 다른 사이트)의 웹 페이지가 우리 API를 호출하는 것을 기본으로 막습니다. 우리 프런트엔드가 `http://localhost:3000`에서 돌고 API가 `8000`번 포트에서 돈다면 둘은 출처가 달라서 막혀요. 서버가 "이 출처는 허락한다"고 응답 헤더로 알려 주는 규칙이 **CORS**(Cross-Origin Resource Sharing)이고, FastAPI에서는 `CORSMiddleware`로 설정합니다.

```python
import os
import secrets

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

# 비밀 값은 코드가 아니라 환경 변수에서 읽는다
API_KEY = os.environ.get("BLOG_API_KEY", "dev-only-key")
허용_출처 = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=허용_출처,
    allow_methods=["GET", "POST"],
    allow_headers=["X-API-Key", "Content-Type"],
)


def 관리자_확인(x_api_key: str | None = Header(default=None)) -> None:
    if x_api_key is None or not secrets.compare_digest(x_api_key, API_KEY):
        raise HTTPException(status_code=401, detail="API 키가 올바르지 않습니다")


@app.get("/api/posts")
def 글_목록():
    return {"글": ["첫 글", "둘째 글"]}


@app.post("/api/posts", status_code=201, dependencies=[Depends(관리자_확인)])
def 글_쓰기():
    return {"결과": "등록되었습니다"}


client = TestClient(app)
print(client.post("/api/posts").status_code, client.post("/api/posts").json())
print(client.post("/api/posts", headers={"X-API-Key": API_KEY}).status_code)

for 출처 in ("http://localhost:3000", "http://evil.example"):
    응답 = client.options(
        "/api/posts",
        headers={"Origin": 출처, "Access-Control-Request-Method": "POST"},
    )
    print(출처, 응답.status_code, 응답.headers.get("access-control-allow-origin"))
```

```text
401 {'detail': 'API 키가 올바르지 않습니다'}
201
http://localhost:3000 200 http://localhost:3000
http://evil.example 400 None
```

`관리자_확인`의 인자 `x_api_key`는 `Header()`로 선언해서 요청 **헤더**에서 값을 받습니다. 파이썬 이름의 밑줄은 헤더 이름의 하이픈으로 바뀌어 `X-API-Key` 헤더를 읽어요. 이 의존성은 돌려줄 값이 없으니 경로 함수 인자 대신 `dependencies=[...]`에 넣었습니다. 키 없이 보낸 요청은 경로 함수에 닿기도 전에 `401`로 돌아왔고, 맞는 키를 보내자 `201`이 됐죠.

아래 두 줄은 브라우저가 실제 요청 전에 "이 출처에서 POST 보내도 되나요?" 하고 먼저 물어보는 **사전 요청(preflight)** 을 흉내 낸 것입니다. 허용 목록에 있는 `localhost:3000`에는 `access-control-allow-origin` 헤더로 허락이 돌아왔고, 목록에 없는 출처는 `400`과 함께 허락 헤더가 없습니다. 허락 헤더가 없으면 브라우저가 실제 요청을 보내지 않아요.

개발용 키를 `dev-only-key`처럼 영어로 지은 데도 이유가 있습니다. 헤더 값에는 ASCII 문자만 쓸 수 있어서, 키를 한글로 지으면 TestClient가 요청을 보내기도 전에 `UnicodeEncodeError`를 냅니다.

> **Q. `allow_origins=["*"]`로 다 열어 두면 편하지 않나요?**  
> 개발 중에는 편하지만, 그러면 아무 사이트의 페이지나 우리 API를 호출할 수 있게 됩니다. CORS는 "어떤 사이트의 페이지가 브라우저 안에서 우리 API를 부를 수 있는가"를 정하는 장치라서, 실제 서비스에서는 우리 프런트엔드 주소만 적는 것이 원칙입니다. 덧붙여 CORS는 브라우저가 지키는 규칙이라 파이썬 프로그램이나 `curl` 같은 도구는 막지 못합니다. 누가 호출하든 막아야 하는 기능은 위의 API 키처럼 서버에서 직접 확인해야 해요.

---

## 실습 프로젝트: 한국형 블로그 시스템

지금까지 배운 것을 모아 블로그 API를 만들어 봅시다. 글 목록·검색, 글쓰기, 읽기(조회수 증가), 부분 수정, 삭제를 지원하고, 데이터는 18장에서 배운 `sqlite3`로 파일에 저장합니다. 서버를 껐다 켜도 글이 남아 있게요.

### 프로젝트 구조

역할별로 파일을 나눕니다. 14장에서 배운 모듈 나누기 그대로예요.

```text
korean_blog/
├── database.py   # sqlite3 연결과 테이블 생성
├── models.py     # 요청·응답 모양 (Pydantic 모델)
├── main.py       # API 경로 함수
└── try_blog.py   # 서버 없이 API 확인하기
```

### 데이터베이스 연결 (database.py)

19.4절의 `yield` 의존성으로 "요청 하나에 연결 하나"를 만들고, 응답이 끝나면 반드시 닫습니다.

```python
# database.py - sqlite3 연결 관리 (17장에서 배운 방식 그대로)
import os
import sqlite3
from collections.abc import Iterator
from pathlib import Path

DB_PATH = Path(os.environ.get("BLOG_DB", "blog.db"))


def 테이블_만들기() -> None:
    with sqlite3.connect(DB_PATH) as 연결:
        연결.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT NOT NULL,
                content    TEXT NOT NULL,
                author     TEXT NOT NULL,
                category   TEXT NOT NULL,
                tags       TEXT NOT NULL DEFAULT '',
                views      INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )
        """)


def 연결_얻기() -> Iterator[sqlite3.Connection]:
    """요청 하나에 연결 하나: 응답이 끝나면 반드시 닫는다."""
    연결 = sqlite3.connect(DB_PATH, check_same_thread=False)
    연결.row_factory = sqlite3.Row  # 행을 열 이름으로 읽을 수 있게
    try:
        yield 연결
    finally:
        연결.close()
```

`sqlite3` 연결은 기본적으로 자기를 만든 스레드에서만 쓰게 되어 있습니다. FastAPI 공식 문서는 한 요청 안에서도 의존성과 경로 함수가 다른 스레드를 쓸 수 있다고 설명하면서 `check_same_thread=False`를 권합니다. 대신 연결을 요청마다 새로 만들고 닫으니, 한 연결을 여러 요청이 나눠 쓰는 일은 없어요. 데이터베이스 파일 위치는 환경 변수 `BLOG_DB`로 바꿀 수 있게 해서, 연습할 때는 임시 파일을 쓸 수 있게 했습니다.

### 데이터 모델 (models.py)

```python
# models.py - 요청과 응답의 모양 (8장의 Pydantic)
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Category = Literal["일상", "여행", "맛집", "개발"]


class PostIn(BaseModel):
    """글을 쓸 때 클라이언트가 보내는 값"""
    title: str = Field(min_length=2, max_length=100)
    content: str = Field(min_length=10)
    author: str = Field(min_length=2, max_length=20)
    category: Category = "일상"
    tags: list[str] = Field(default_factory=list, max_length=5)


class PostUpdate(BaseModel):
    """PATCH용: 보낸 값만 바꾸고, 빠진 값(None)은 그대로 둔다"""
    title: str | None = Field(default=None, min_length=2, max_length=100)
    content: str | None = Field(default=None, min_length=10)
    category: Category | None = None
    tags: list[str] | None = Field(default=None, max_length=5)


class Post(PostIn):
    """서버가 돌려주는 글: 입력값 + 서버가 정하는 값"""
    id: int
    views: int
    created_at: datetime
```

19.6절처럼 입력(`PostIn`)과 출력(`Post`)을 나눴고, 부분 수정용 `PostUpdate`를 하나 더 만들었습니다. `PostUpdate`의 필드는 모두 `None`이 기본값이라 바꿀 필드만 보내면 됩니다. `category`의 타입 `Literal[...]`(2장)은 "이 네 값 중 하나만 받는다"는 뜻이에요. 목록에 없는 카테고리를 보내면 422가 됩니다. 이번에는 필드 이름도 영어로 지었습니다. 데이터베이스 열 이름과 그대로 맞출 수 있고, 다른 언어로 만든 프런트엔드가 쓰기에도 편하니까요.

### 메인 애플리케이션 (main.py)

```python
# main.py - 한국형 블로그 API
import sqlite3

from fastapi import Depends, FastAPI, HTTPException, Query, status

from database import 연결_얻기, 테이블_만들기
from models import Category, Post, PostIn, PostUpdate

app = FastAPI(title="한국형 블로그 API", version="1.0.0")
테이블_만들기()


def 행을_글로(행: sqlite3.Row) -> Post:
    태그들 = 행["tags"].split(",") if 행["tags"] else []
    return Post(**{**dict(행), "tags": 태그들})


def 글_찾기(post_id: int, db: sqlite3.Connection) -> sqlite3.Row:
    행 = db.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    if 행 is None:
        raise HTTPException(status_code=404, detail=f"{post_id}번 글이 없습니다")
    return 행


@app.get("/api/posts")
def 글_목록(
    category: Category | None = None,
    q: str | None = Query(default=None, min_length=1),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=50),
    db: sqlite3.Connection = Depends(연결_얻기),
) -> list[Post]:
    조건, 값들 = [], []
    if category:
        조건.append("category = ?")
        값들.append(category)
    if q:
        조건.append("(title LIKE ? OR content LIKE ?)")
        값들 += [f"%{q}%", f"%{q}%"]
    sql = "SELECT * FROM posts"
    if 조건:
        sql += " WHERE " + " AND ".join(조건)  # 조각은 모두 위에 고정된 문자열
    sql += " ORDER BY id DESC LIMIT ? OFFSET ?"
    값들 += [size, (page - 1) * size]
    return [행을_글로(행) for 행 in db.execute(sql, 값들)]


@app.post("/api/posts", status_code=status.HTTP_201_CREATED)
def 글_쓰기(입력: PostIn, db: sqlite3.Connection = Depends(연결_얻기)) -> Post:
    커서 = db.execute(
        "INSERT INTO posts (title, content, author, category, tags)"
        " VALUES (?, ?, ?, ?, ?)",
        (입력.title, 입력.content, 입력.author, 입력.category, ",".join(입력.tags)),
    )
    db.commit()
    return 행을_글로(글_찾기(커서.lastrowid, db))


@app.get("/api/posts/{post_id}")
def 글_읽기(post_id: int, db: sqlite3.Connection = Depends(연결_얻기)) -> Post:
    글_찾기(post_id, db)
    db.execute("UPDATE posts SET views = views + 1 WHERE id = ?", (post_id,))
    db.commit()
    return 행을_글로(글_찾기(post_id, db))


@app.patch("/api/posts/{post_id}")
def 글_고치기(
    post_id: int, 입력: PostUpdate, db: sqlite3.Connection = Depends(연결_얻기)
) -> Post:
    글_찾기(post_id, db)
    태그 = ",".join(입력.tags) if 입력.tags is not None else None
    # COALESCE(새 값, 원래 값): 새 값이 NULL(None)이면 원래 값을 유지
    db.execute(
        """UPDATE posts SET title = COALESCE(?, title), content = COALESCE(?, content),
               category = COALESCE(?, category), tags = COALESCE(?, tags)
           WHERE id = ?""",
        (입력.title, 입력.content, 입력.category, 태그, post_id),
    )
    db.commit()
    return 행을_글로(글_찾기(post_id, db))


@app.delete("/api/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def 글_지우기(post_id: int, db: sqlite3.Connection = Depends(연결_얻기)) -> None:
    글_찾기(post_id, db)
    db.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    db.commit()
```

이 장에서 배운 것이 전부 들어 있습니다. 몇 군데만 짚어 볼게요.

- **쿼리 매개변수 제약**: `Query(default=1, ge=1)`처럼 쓰면 쿼리 매개변수에도 `Field`처럼 범위를 걸 수 있습니다. `size=1000`으로 한꺼번에 많은 글을 긁어 가는 요청은 422로 막혀요.
- **검색 SQL 조립**: 조건에 따라 `WHERE` 절을 붙이지만, 이어 붙이는 조각은 모두 코드에 고정된 문자열이고 사용자 입력(`category`, `q`)은 전부 `?` 자리로만 들어갑니다. 19.7절의 원칙 그대로죠.
- **부분 수정**: SQLite의 `COALESCE(a, b)`는 `a`가 `NULL`이면 `b`를 돌려줍니다. 보내지 않은 필드는 `None`, 즉 `NULL`로 들어가니 원래 값이 유지돼요. 덕분에 "어떤 열을 바꿀지"에 따라 SQL을 조립할 필요가 없습니다.
- **태그 저장**: 태그 목록은 쉼표로 이어 한 칸에 저장하고, 꺼낼 때 다시 나눕니다. 태그 하나하나로 검색해야 한다면 18장의 정규화처럼 태그 테이블을 따로 두는 것이 정석입니다.

### 블로그 API 확인하기 (try_blog.py)

서버를 띄우지 않고 전체 흐름을 확인해 봅시다. 먼저 환경 변수 `BLOG_DB`를 임시 폴더의 새 파일로 정해서, 실행할 때마다 빈 데이터베이스로 시작하게 했습니다. `main`을 가져오기 **전에** 정해야 `database.py`가 그 값을 읽어요.

```python
# try_blog.py - 서버를 띄우지 않고 블로그 API 확인하기
import os
import tempfile
from pathlib import Path

os.environ["BLOG_DB"] = str(Path(tempfile.mkdtemp()) / "blog.db")  # 연습용 새 DB

from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402

client = TestClient(app)

새_글들 = [
    {"title": "부산 돼지국밥 투어", "content": "서면에서 시작해 남포동까지 걸었어요.",
     "author": "김부산", "category": "맛집", "tags": ["부산", "국밥"]},
    {"title": "FastAPI 첫걸음", "content": "타입 힌트만으로 검증이 되다니 놀랍네요.",
     "author": "이개발", "category": "개발", "tags": ["파이썬"]},
    {"title": "제주 올레길 7코스", "content": "외돌개에서 시작하는 바닷길입니다.",
     "author": "박제주", "category": "여행"},
]
for 글 in 새_글들:
    응답 = client.post("/api/posts", json=글)
    print(응답.status_code, 응답.json()["id"], 응답.json()["title"])

목록 = client.get("/api/posts", params={"size": 2}).json()
print("최신 2개:", [글["title"] for 글 in 목록])
print("맛집:", [글["title"] for 글 in client.get("/api/posts?category=맛집").json()])
print("검색:", [글["title"] for 글 in client.get("/api/posts?q=바닷길").json()])

client.get("/api/posts/1")
글 = client.get("/api/posts/1").json()
print("조회수:", 글["views"], "태그:", 글["tags"])

글 = client.patch("/api/posts/2", json={"title": "FastAPI 두 번째 걸음"}).json()
print("수정:", 글["title"], "/", 글["content"])

print("삭제:", client.delete("/api/posts/3").status_code)
print("다시 조회:", client.get("/api/posts/3").json())

응답 = client.post("/api/posts", json={"title": "짧", "content": "짧아요",
                                        "author": "최", "category": "운동"})
print(응답.status_code, [오류["loc"][-1] for 오류 in 응답.json()["detail"]])
```

```text
201 1 부산 돼지국밥 투어
201 2 FastAPI 첫걸음
201 3 제주 올레길 7코스
최신 2개: ['제주 올레길 7코스', 'FastAPI 첫걸음']
맛집: ['부산 돼지국밥 투어']
검색: ['제주 올레길 7코스']
조회수: 2 태그: ['부산', '국밥']
수정: FastAPI 두 번째 걸음 / 타입 힌트만으로 검증이 되다니 놀랍네요.
삭제: 204
다시 조회: {'detail': '3번 글이 없습니다'}
422 ['title', 'content', 'author', 'category']
```

결과를 하나씩 맞춰 보세요. 목록은 최신 글부터 `size`개만 왔고, 카테고리 필터와 본문 검색이 동작합니다. 1번 글을 두 번 읽었더니 조회수가 2가 됐고, 쉼표로 저장한 태그는 다시 목록으로 돌아왔어요. `PATCH`로 제목만 보냈더니 내용은 그대로 남았습니다. 마지막 요청은 네 필드가 모두 규칙을 어겨서 네 곳이 한꺼번에 지적됐죠. 카테고리 `운동`은 `Literal` 목록에 없어서 걸렸습니다.

서버로 띄워 보고 싶다면 `korean_blog` 폴더에서 `uv run fastapi dev main.py`를 실행하고 `http://127.0.0.1:8000/docs`를 열어 보세요. 다섯 개의 API가 메뉴판에 정리되어 있고, 화면에서 바로 글을 써 볼 수 있습니다.

---

## 연습문제

### 기초 문제 (1-5번)

**1번:** HTTP 메서드와 용도를 짝지으세요.
```python
# 다음 상황에 적합한 HTTP 메서드를 고르세요
상황들 = [
    "한국 맛집 목록을 가져올 때",
    "새로운 리뷰를 작성할 때",
    "기존 맛집 정보를 완전히 수정할 때",
    "맛집의 평점만 업데이트할 때",
    "리뷰를 삭제할 때"
]

# 정답을 작성해보세요
답안 = {
    "맛집 목록 가져오기": "?",
    "리뷰 작성": "?",
    "맛집 정보 완전 수정": "?",
    "평점만 업데이트": "?",
    "리뷰 삭제": "?"
}
```

**2번:** 다음 주소를 처리하는 경로 함수를 완성하세요. 경로 매개변수 이름은 영어로 짓는다는 점을 잊지 마세요.
```python
from fastapi import FastAPI

app = FastAPI()

# TODO: 다음 주소들을 처리하는 경로 함수를 작성하세요
# /users/123                                    -> 사용자 ID 123의 정보 조회
# /search/서울/카페                              -> 서울의 카페 검색
# /api/products?category=전자제품&min_price=10000 -> 조건에 맞는 상품 조회


@app.get("/users/{user_id}")
def 사용자_정보(user_id: int):
    # TODO: {"사용자_id": user_id} 를 돌려주세요
    pass

# 나머지 경로 함수들을 작성해보세요
```

**3번:** 모든 API가 같은 모양으로 응답하도록 응답 모델을 만드세요.
```python
from datetime import datetime

from pydantic import BaseModel


class ApiResponse(BaseModel):
    """
    표준화된 API 응답

    {
        "상태": "성공" 또는 "실패",
        "메시지": 설명 문장,
        "데이터": 실제 데이터 (없으면 None),
        "시간": 응답을 만든 시각
    }
    """
    # TODO: 위 형식에 맞게 필드를 정의하세요
    # 힌트: 시간은 Field(default_factory=datetime.now)
    pass


def 응답_생성(데이터=None, 메시지: str = "성공") -> ApiResponse:
    # TODO: ApiResponse 객체를 만들어 돌려주세요
    pass
```

**4번:** 입력값 검증 함수들을 완성하세요. 다 만들었다면 같은 규칙을 Pydantic `Field(pattern=...)`로도 표현해 보세요.
```python
import re

def 한국_휴대폰번호_검증(번호: str) -> bool:
    """한국 휴대폰 번호 형식 검증 (010-0000-0000)"""
    # TODO: 정규식을 사용하여 검증하세요
    pass

def 한국어_이름_검증(이름: str) -> bool:
    """한국어 이름 검증 (2-10자, 한글만)"""
    # TODO: 한글 2-10자 검증하세요
    pass

def 이메일_검증(이메일: str) -> bool:
    """이메일 형식 검증"""
    # TODO: 기본적인 이메일 형식을 검증하세요
    pass

# 테스트
print(한국_휴대폰번호_검증("010-1234-5678"))  # True
print(한국어_이름_검증("김철수"))  # True
print(이메일_검증("test@example.com"))  # True
```

**5번:** 회원 가입 요청 모델을 만들고, 응답에는 비밀번호가 나가지 않게 하세요.
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class SignUpIn(BaseModel):
    # TODO: 아이디(4-20자), 이름(2-10자), 비밀번호(8자 이상) 필드를 정의하세요
    pass


class UserOut(BaseModel):
    # TODO: 응답에 내보낼 필드만 정의하세요 (비밀번호 제외)
    pass


@app.post("/api/users", status_code=201)
def 회원_가입(입력: SignUpIn) -> UserOut:
    # TODO: 18.7절의 비밀번호_해시()로 해시를 만들어 저장하고 UserOut을 돌려주세요
    pass
```

### 중급 문제 (6-10번)

**6번:** RESTful API 설계하기
```python
"""
한국 도서관 시스템을 위한 RESTful API를 설계하세요.

요구사항:
- 도서 목록 조회, 등록, 수정, 삭제
- 사용자 목록 조회, 등록
- 도서 대출/반납 기능
- 대출 현황 조회

다음 엔드포인트들을 설계하고 구현하세요:
1. GET /api/books - 도서 목록 조회
2. POST /api/books - 새 도서 등록
3. GET /api/books/{book_id} - 도서 상세 조회
4. PUT /api/books/{book_id} - 도서 정보 수정
5. POST /api/books/{book_id}/borrow - 도서 대출 (이미 대출 중이면 409)
6. POST /api/books/{book_id}/return - 도서 반납
7. GET /api/users/{user_id}/borrowed - 사용자 대출 현황
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="한국 도서관 API")

# TODO: 위의 요구사항에 맞는 모델과 API를 구현하세요
```

**7번:** 파일 업로드 처리하기 (`fastapi[standard]`에 포함된 `python-multipart`가 필요합니다)
```python
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile

app = FastAPI()

# 허용되는 파일 확장자
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".pdf"}
MAX_SIZE = 5 * 1024 * 1024  # 5MB


def 허용된_파일인가(filename: str) -> bool:
    """파일 확장자 검증"""
    # TODO: Path(filename).suffix를 이용해 확장자가 허용되는지 검증하세요
    pass


@app.post("/api/upload", status_code=201)
async def 파일_업로드(file: UploadFile):
    """
    파일 업로드 처리
    - 확장자 검사 (허용되지 않으면 400)
    - 파일 크기 제한 5MB (넘으면 413)
    - 한글 파일명 지원, 경로 문자(../) 제거
    - 저장한 파일 이름과 크기를 응답
    """
    # TODO: 내용은 await file.read()로 읽습니다
    pass
```

**8번:** 토큰 로그인 구현하기
```python
import secrets

from fastapi import Depends, FastAPI, Header, HTTPException

app = FastAPI()

토큰_저장소: dict[str, str] = {}  # 토큰 -> 사용자 아이디


@app.post("/api/login")
def 로그인(아이디: str, 비밀번호: str):
    """
    - 비밀번호를 확인하고 secrets.token_urlsafe()로 토큰 발급
    - 토큰_저장소에 기록하고 토큰을 응답
    - 틀리면 401
    """
    # TODO
    pass


def 로그인_사용자(authorization: str | None = Header(default=None)) -> str:
    """'Bearer 토큰' 형식의 헤더를 확인해 사용자 아이디를 돌려주는 의존성"""
    # TODO: 없거나 모르는 토큰이면 401
    pass


@app.get("/api/profile")
def 프로필(사용자: str = Depends(로그인_사용자)):
    # TODO: 로그인한 사용자의 정보를 돌려주세요
    pass


@app.post("/api/logout")
def 로그아웃(authorization: str | None = Header(default=None)):
    # TODO: 토큰_저장소에서 토큰을 지우세요
    pass
```

**9번:** 페이지네이션 구현하기
```python
import math

from fastapi import FastAPI, Query

app = FastAPI()

# 샘플 데이터 (한국 도시 100개)
한국_도시들 = [f"도시_{i}" for i in range(1, 101)]


def 페이지네이션(데이터_리스트: list, 페이지: int = 1, 페이지_크기: int = 10) -> dict:
    """
    Returns:
        {
            "데이터": 현재 페이지 데이터,
            "페이지정보": {
                "현재_페이지": 페이지,
                "총_페이지수": 총 페이지 수,
                "총_항목수": 전체 항목 수,
                "페이지_크기": 페이지 크기,
                "이전_페이지": 이전 페이지 번호 (없으면 None),
                "다음_페이지": 다음 페이지 번호 (없으면 None)
            }
        }
    """
    # TODO: 페이지네이션 로직을 구현하세요 (math.ceil 활용)
    pass


@app.get("/api/cities")
def 도시_목록(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=50),
):
    # TODO: 페이지네이션을 적용한 결과를 돌려주세요
    pass
```

**10번:** 에러 처리와 로깅
```python
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()
logger = logging.getLogger("korean_api")


class 재고부족오류(Exception):
    def __init__(self, 상품명: str):
        self.상품명 = 상품명


@app.exception_handler(재고부족오류)
async def 재고부족_처리(request: Request, exc: 재고부족오류) -> JSONResponse:
    # TODO: 409 상태 코드와 {"detail": "○○ 재고가 부족합니다"}를 돌려주고
    #       경고 로그를 남기세요
    pass


@app.exception_handler(Exception)
async def 예상못한_오류_처리(request: Request, exc: Exception) -> JSONResponse:
    # TODO: 500 상태 코드와 내부 정보가 드러나지 않는 메시지를 돌려주고,
    #       로그에는 자세히 남기세요
    pass


@app.post("/api/orders")
def 주문():
    raise 재고부족오류("무선 이어폰")
```

### 고급 문제 (11-12번)

**11번:** 실습 프로젝트의 블로그에 댓글 기능을 추가하세요. `comments` 테이블을 만들어 `post_id`로 글과 연결하고, `GET`/`POST /api/posts/{post_id}/comments`를 구현합니다. 없는 글에 댓글을 달면 404, 글을 지우면 댓글도 함께 지워져야 합니다. TestClient로 각 경우의 상태 코드를 확인하는 `try_comments.py`도 작성하세요.

**12번:** 블로그에 회원 기능을 붙이세요. 19.7절의 `비밀번호_해시()`로 가입한 회원을 `users` 테이블에 저장하고, 8번 문제의 토큰 방식으로 로그인하게 합니다. 글쓰기·수정·삭제는 로그인한 사용자만, 수정·삭제는 자기 글만 할 수 있게(남의 글이면 403) 의존성으로 구현하세요. 응답 어디에도 비밀번호 해시가 나가지 않는지 `/openapi.json`의 스키마로 확인해 보세요.

---

## 정리 및 다음 단계

### 이번 장에서 배운 것들

1. **HTTP**: 클라이언트와 서버는 메서드·주소·헤더·본문으로 이루어진 요청과, 상태 코드·헤더·본문으로 이루어진 응답을 주고받습니다.
2. **FastAPI 기초**: 데코레이터로 주소와 경로 함수를 짝짓고, 딕셔너리나 모델을 돌려주면 JSON 응답이 됩니다. `TestClient`로 서버 없이 확인할 수 있어요.
3. **경로·쿼리 매개변수**: 타입 힌트대로 변환·검사되고, 틀리면 422가 돌아갑니다.
4. **의존성 주입과 자동 문서**: 공통 준비 작업은 `Depends`로 나누고, `/docs`와 `/openapi.json`의 명세는 코드에서 자동으로 만들어집니다.
5. **Pydantic 요청 검증**: 요청 본문의 양식을 모델로 정의하면 검사와 변환을 FastAPI가 맡습니다.
6. **RESTful API**: 명사 주소 + 메서드 동사, 그리고 결과에 맞는 상태 코드와 `HTTPException`.
7. **보안 기본**: 입력 검증, SQL 자리표시자, 소금 친 비밀번호 해시, 환경 변수, API 키 의존성, CORS.

### 실무 적용 팁

- **보안**: 사용자 입력은 모델로 검증하고, 비밀 값은 환경 변수로 관리하고, 실제 서비스는 HTTPS로 운영하고, CORS 허용 출처는 꼭 필요한 곳만 적습니다.
- **설계**: 입력 모델과 출력 모델을 나누고, 상태 코드로 결과를 말하게 합니다. 목록 API에는 처음부터 페이지 나누기를 넣으세요. 데이터가 쌓인 뒤에 넣으면 API를 쓰는 쪽이 모두 바뀌어야 합니다.
- **유지보수**: 경로 함수에는 요청 처리만 두고, 데이터베이스 연결·인증 같은 공통 작업은 의존성으로 뺍니다. API를 고칠 때마다 `TestClient` 확인 스크립트를 함께 돌리면, 고친 곳이 다른 곳을 깨뜨리지 않았는지 바로 알 수 있습니다.

### 다음 단계

웹 API를 만들 수 있게 되면 데이터가 쌓이기 시작합니다. 블로그의 글과 조회수, 쇼핑몰의 상품과 주문 기록 같은 것들이죠. 그런데 쌓인 데이터에서 "어떤 카테고리 글이 많이 읽히나?", "어느 요일에 주문이 몰리나?" 같은 답을 꺼내려면 또 다른 도구가 필요합니다.

다음 20장에서는 NumPy와 pandas로 이런 데이터를 정리·분석하고, Matplotlib으로 그래프를 그립니다. 20장의 종합 프로젝트가 바로 온라인 쇼핑몰 데이터 분석이에요. 이 장에서 만든 쇼핑몰 API가 쌓을 법한 데이터를 분석하는 쪽으로 넘어가는 셈입니다. 그리고 2권(딥러닝 편)의 종합 프로젝트인 맛집 추천 AI 플랫폼에서 FastAPI가 백엔드로 다시 등장합니다.

---
