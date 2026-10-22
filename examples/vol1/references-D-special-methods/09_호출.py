"""1권 레퍼런스 D. 특수 메서드 — 호출

원고: manuscript/references/D-special-methods.md (269줄부터)
"""

# ---- 원고 269줄 ----
class VatCalculator:
    def __init__(self, rate: float) -> None:
        self.rate = rate

    def __call__(self, price: int) -> int:    # 객체를 함수처럼 부르기
        return round(price * (1 + self.rate))

vat = VatCalculator(0.1)
print(vat(10000), callable(vat))   # 11000 True
