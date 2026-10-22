# [1권 Chapter 14: 모듈과 패키지 · 14.3 모듈의 고급 기능 · manuscript/chapters/14-modules-packages.md:340]
# test_public_api.py
from cafe_utils_v2 import *

# __all__에 정의된 것만 import됨
print("사용 가능한 함수들:")
try:
    calculate_total([])  # 성공
    print("[O] calculate_total")
except NameError:
    print("[X] calculate_total")

try:
    _validate_price(100)  # 실패 - private 함수
    print("[O] _validate_price")
except NameError:
    print("[X] _validate_price (private)")
