"""1권 레퍼런스 D. 특수 메서드 — 컨텍스트 매니저

원고: manuscript/references/D-special-methods.md (426줄부터)
"""

# ---- 원고 426줄 ----
class Transaction:
    def __enter__(self) -> "Transaction":
        print("거래 시작")
        return self                           # as 뒤의 이름에 담김

    def __exit__(self, exc_type, exc, tb) -> bool:
        print("롤백" if exc_type else "커밋")
        return exc_type is ValueError         # True면 예외를 삼킴

with Transaction():
    print("이체 1만 원")
with Transaction():
    raise ValueError("잔액 부족")
print("계속 실행")
# 거래 시작 / 이체 1만 원 / 커밋 / 거래 시작 / 롤백 / 계속 실행 (한 줄씩 출력)
