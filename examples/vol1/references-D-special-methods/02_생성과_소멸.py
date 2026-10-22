"""1권 레퍼런스 D. 특수 메서드 — 생성과 소멸

원고: manuscript/references/D-special-methods.md (39줄부터)
"""

# ---- 원고 39줄 ----
class Won(int):
    """음수가 될 수 없는 금액(int를 상속)"""

    def __new__(cls, amount: int) -> "Won":
        if amount < 0:
            raise ValueError("금액은 0 이상이어야 해요")
        return super().__new__(cls, amount)   # 바꿀 수 없는 int는 __new__에서 값을 정함

    def __init__(self, amount: int) -> None:
        self.currency = "KRW"                 # 이미 만들어진 객체에 속성만 채움

price = Won(5000)
print(price + 1000, price.currency, isinstance(price, int))   # 6000 KRW True
