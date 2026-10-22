"""1권 레퍼런스 D. 특수 메서드 — 디스크립터

원고: manuscript/references/D-special-methods.md (202줄부터)
"""

# ---- 원고 202줄 ----
class Positive:
    def __set_name__(self, owner: type, name: str) -> None:   # 클래스에 붙는 순간
        self.name = "_" + name

    def __get__(self, obj: object, objtype: type | None = None) -> object:
        if obj is None:
            return self                       # 클래스에서 읽으면 디스크립터 자신
        return getattr(obj, self.name)

    def __set__(self, obj: object, value: int) -> None:
        if value < 0:
            raise ValueError(f"{self.name[1:]}은(는) 0 이상이어야 해요")
        setattr(obj, self.name, value)

class Coffee:
    price = Positive()

    def __init__(self, price: int) -> None:
        self.price = price                    # Positive.__set__이 불림

c = Coffee(4500)
print(c.price, type(Coffee.__dict__["price"]).__name__)   # 4500 Positive
try:
    c.price = -1
except ValueError as e:
    print("[X]", e)                           # [X] price은(는) 0 이상이어야 해요
