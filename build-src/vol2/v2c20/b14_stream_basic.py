import time
from collections.abc import Iterator

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.testclient import TestClient

app = FastAPI()


def 조각_만들기() -> Iterator[str]:
    for 조각 in ["오늘은 ", "비가 ", "와서 ", "우산을 ", "챙겼어요."]:
        time.sleep(0.2)                      # 다음 조각을 만드는 데 걸리는 시간
        yield 조각


@app.get("/whole")
def 한꺼번에() -> dict:
    return {"text": "".join(조각_만들기())}  # 다 만든 뒤에 한 번에 보낸다


@app.get("/stream")
def 흘려보내기() -> StreamingResponse:
    return StreamingResponse(조각_만들기(), media_type="text/plain; charset=utf-8")


client = TestClient(app)
시작 = time.perf_counter()
본문 = client.get("/whole").json()["text"]
print(f"[/whole ] {time.perf_counter() - 시작:.1f}초 뒤 한꺼번에: {본문!r}")

시작 = time.perf_counter()
with client.stream("GET", "/stream") as 응답:
    print("[/stream]", 응답.headers["content-type"])
    for 조각 in 응답.iter_text():
        print(f"  {time.perf_counter() - 시작:.1f}초: {조각!r}")
