"""1권 레퍼런스 D. 특수 메서드 — 클래스 만들기

원고: manuscript/references/D-special-methods.md (244줄부터)
"""

# ---- 원고 244줄 ----
class Plugin:
    registry: dict[str, type] = {}

    def __init_subclass__(cls, /, key: str, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Plugin.registry[key] = cls            # 자식 클래스가 정의될 때마다 등록

    def __class_getitem__(cls, item: type) -> str:   # Plugin[int] 문법
        return f"{cls.__name__}[{item.__name__}]"

class CsvExport(Plugin, key="csv"): pass
class JsonExport(Plugin, key="json"): pass

print(Plugin.registry)
# {'csv': <class '__main__.CsvExport'>, 'json': <class '__main__.JsonExport'>}
print(Plugin[int])     # Plugin[int]
