"""1권 레퍼런스 C. 예외 계층 — 예외 그룹과 `except*` (3.11+)

원고: manuscript/references/C-exception-hierarchy.md (206줄부터)
"""

# ---- 원고 206줄 ----
def load_all():
    errors = []
    for raw in ['1', 'x', None]:
        try:
            int(raw)
        except (ValueError, TypeError) as e:
            errors.append(e)
    if errors:
        raise ExceptionGroup('변환 실패', errors)

try:
    load_all()
except* ValueError as group:
    print('값 오류', len(group.exceptions), '개')    # 값 오류 1 개
except* TypeError as group:
    print('타입 오류', len(group.exceptions), '개')  # 타입 오류 1 개
