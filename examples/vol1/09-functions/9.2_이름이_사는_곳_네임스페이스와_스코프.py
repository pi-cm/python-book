"""1권 Chapter 9: 함수 — 9.2 이름이 사는 곳: 네임스페이스와 스코프

원고: manuscript/chapters/09-functions.md (199줄부터)
"""

# ---- 원고 199줄 ----
a = "global"

def outer_func():
    a = "outer"

    def inner_func():
        a = "inner"
        print(f"inner_func: {a}")
        print(f"inner_func의 이름들: {locals()}")

    inner_func()
    print(f"outer_func: {a}")

outer_func()
print(f"모듈: {a}")

# ---- 원고 225줄 ----
count = 0

def increase():
    count += 1          # 지역 변수 count에 아직 값이 없는데 1을 더하려 함

try:
    increase()
except UnboundLocalError as e:
    print(f"[X] {e}")

# 권장: 바깥 값은 매개변수로 받고, 결과는 return으로 돌려준다
def increase_from(value):
    return value + 1

count = increase_from(count)
print(f"[O] count = {count}")  # [O] count = 1
