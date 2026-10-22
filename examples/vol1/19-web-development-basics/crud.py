# [1권 Chapter 19: 웹 개발 기초 · 19.6 RESTful API 설계와 구현 · manuscript/chapters/19-web-development-basics.md:462]
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
