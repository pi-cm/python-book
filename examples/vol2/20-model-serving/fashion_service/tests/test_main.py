# [2권 Chapter 20. FastAPI로 모델 서빙: 내 모델을 웹 서비스로 · 20.11 실습: 옷 사진 분류 서비스 완성하기 · manuscript-vol2/chapters/20-model-serving.md:1323]
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
