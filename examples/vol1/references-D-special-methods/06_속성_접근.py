"""1권 레퍼런스 D. 특수 메서드 — 속성 접근

원고: manuscript/references/D-special-methods.md (165줄부터)
"""

# ---- 원고 165줄 ----
class Settings:
    def __init__(self) -> None:
        super().__setattr__("_data", {})      # __setattr__를 거치지 않고 저장

    def __getattr__(self, name: str) -> object:   # 평소대로 찾아서 없을 때만
        return self._data.get(name)

    def __setattr__(self, name: str, value: object) -> None:  # 모든 대입
        self._data[name] = value

    def __delattr__(self, name: str) -> None:
        self._data.pop(name, None)

    def __dir__(self) -> list[str]:
        return sorted(self._data)

s = Settings()
s.region = "서울"
print(s.region, s.timeout, dir(s))   # 서울 None ['region']
del s.region
print(s.region)                      # None
