"""1권 레퍼런스 C. 예외 계층 — 내장 예외 트리

원고: manuscript/references/C-exception-hierarchy.md (89줄부터)
"""

# ---- 원고 89줄 ----
def show(cls, depth=0):
    print('    ' * depth + cls.__name__)
    for sub in sorted(cls.__subclasses__(), key=lambda c: c.__name__):
        if sub.__module__ == 'builtins':
            show(sub, depth + 1)

show(BaseException)
