"""맛집 추천 API 테스트. 실행: uv run pytest -q"""
from collections.abc import Iterator
from typing import get_args

import pytest
from fastapi.testclient import TestClient

from app.main import Area, app, 추천기_얻기
from app.recommender import 추천목록


class 가짜추천기:
    """식당 세 곳만 아는 가짜. 진짜 벡터 없이 API의 모양과 오류 처리만 시험한다."""
    지역들 = list(get_args(Area))
    식당 = [{"id": i, "name": f"가짜 식당 {i}", "area": "성수", "cuisine": "한식", "price": 1}
           for i in range(3)]

    def 사용자_수(self) -> int:
        return 2

    def 추천(self, 사용자: int, k: int, 지역: str | None = None) -> tuple[str, 추천목록]:
        return "personal", [(2, 0.9), (0, 0.5)][:k]

    def 새_사용자_추천(self, 동네: str, 가본_곳: list[int], k: int, 지역: str | None = None) -> 추천목록:
        return [(i, 0.1) for i in range(3) if i not in 가본_곳][:k]

    def 비슷한_식당(self, 식당: int, k: int) -> 추천목록:
        return [(i, 0.3) for i in range(3) if i != 식당][:k]


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:                       # with로 열어야 lifespan이 돈다
        yield c


@pytest.fixture
def fake_client(client: TestClient) -> Iterator[TestClient]:
    app.dependency_overrides[추천기_얻기] = 가짜추천기
    yield client
    app.dependency_overrides.clear()


def test_area_literal_matches_catalog(client: TestClient) -> None:
    assert list(get_args(Area)) == app.state.추천기.지역들


def test_recommendations_for_known_user_exclude_visited(client: TestClient) -> None:
    가본_곳 = set(app.state.추천기.사용자[0]["visited"])
    본문 = client.get("/users/0/recommendations", params={"k": 10}).json()
    assert 본문["strategy"] == "personal"
    assert len(본문["items"]) == 10
    assert not {항목["id"] for 항목 in 본문["items"]} & 가본_곳
    점수 = [항목["score"] for 항목 in 본문["items"]]
    assert 점수 == sorted(점수, reverse=True)


def test_recommendations_with_area_filter_return_only_that_area(client: TestClient) -> None:
    본문 = client.get("/users/0/recommendations", params={"area": "이태원"}).json()
    assert {항목["area"] for 항목 in 본문["items"]} == {"이태원"}


def test_recommendations_for_user_without_history_fall_back_to_new_user(client: TestClient) -> None:
    추천기_ = app.state.추천기
    처음_온_사람 = next(u for u in range(추천기_.사용자_수()) if not 추천기_.아는_사용자[u])
    본문 = client.get(f"/users/{처음_온_사람}/recommendations").json()
    assert 본문["strategy"] == "new_user"
    assert len(본문["items"]) == 10


def test_similar_restaurants_exclude_itself(client: TestClient) -> None:
    본문 = client.get("/restaurants/17/similar", params={"k": 5}).json()
    번호들 = [항목["id"] for 항목 in 본문["items"]]
    assert len(번호들) == 5 and 17 not in 번호들


def test_new_user_request_excludes_visited(fake_client: TestClient) -> None:
    본문 = fake_client.post("/recommendations/new-user",
                          json={"home": "성수", "visited": [0], "k": 5}).json()
    assert [항목["id"] for 항목 in 본문["items"]] == [1, 2]


def test_unknown_user_or_restaurant_returns_404(fake_client: TestClient) -> None:
    assert fake_client.get("/users/99/recommendations").status_code == 404
    assert fake_client.get("/restaurants/99/similar").status_code == 404
    응답 = fake_client.post("/recommendations/new-user", json={"home": "성수", "visited": [99]})
    assert 응답.status_code == 404


def test_invalid_k_or_area_returns_422(fake_client: TestClient) -> None:
    assert fake_client.get("/users/0/recommendations", params={"k": 0}).status_code == 422
    assert fake_client.get("/users/0/recommendations", params={"area": "부산"}).status_code == 422
    assert fake_client.post("/recommendations/new-user", json={"home": "부산"}).status_code == 422
