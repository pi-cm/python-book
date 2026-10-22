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
