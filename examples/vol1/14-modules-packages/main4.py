# [1권 Chapter 14: 모듈과 패키지 · 14.2 모듈 불러오기 (Import) · manuscript/chapters/14-modules-packages.md:227]
# main4.py
from cafe_utils import *

# 모든 public 객체를 직접 사용할 수 있음
cafe = CafeManager("전체임포트 카페", "건대")
total = calculate_total([{'price': 4000}])

# 하지만 네임스페이스 오염이 발생할 수 있으므로 권장하지 않음
