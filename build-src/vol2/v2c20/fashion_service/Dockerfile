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
