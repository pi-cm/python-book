"""1권 부록 C. 버전별 새 기능 (3.8~3.14) — C.5 Python 3.11

원고: manuscript/appendix/C-version-features.md (164줄부터)
"""

# ---- 원고 164줄 ----
# Python 3.11 이상
import tomllib
config = tomllib.loads('''
name = "my-app"
[server]
port = 8000
''')
print(config["server"]["port"])   # 8000

def check(values):
    errors = []
    for v in values:
        try:
            int(v)
        except ValueError as e:
            e.add_note(f"입력값: {v!r}")
            errors.append(e)
    if errors:
        raise ExceptionGroup("검사 실패", errors)

try:
    check(["1", "x", "2.5"])
except* ValueError as group:
    for e in group.exceptions:
        print(e.__notes__[0])     # 입력값: 'x' / 입력값: '2.5'
