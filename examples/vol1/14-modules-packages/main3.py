# [1권 Chapter 14: 모듈과 패키지 · 14.2 모듈 불러오기 (Import) · manuscript/chapters/14-modules-packages.md:197]
# main3.py
import cafe_utils as cu
from cafe_utils import CafeManager as CM, DEFAULT_PRICE as DP

# 긴 모듈명을 짧게 사용
cafe = cu.CafeManager("지훈네 카페", "명동")
print(f"기본 가격: {DP}원")

# 클래스명도 짧게 사용
another_cafe = CM("은혜네 카페", "신촌")
