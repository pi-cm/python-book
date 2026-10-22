"""1권 레퍼런스 D. 특수 메서드 — 버퍼 프로토콜

원고: manuscript/references/D-special-methods.md (504줄부터)
"""

# ---- 원고 504줄 ----
from collections.abc import Buffer

class Payload:
    def __init__(self, text: str) -> None:
        self.data = bytearray(text.encode())

    def __buffer__(self, flags: int) -> memoryview:   # memoryview(), bytes()
        return memoryview(self.data)

p = Payload("가")
print(bytes(p), memoryview(p).nbytes, isinstance(p, Buffer))   # b'\xea\xb0\x80' 3 True
