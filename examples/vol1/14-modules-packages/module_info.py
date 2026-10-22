# [1권 Chapter 14: 모듈과 패키지 · 14.3 모듈의 고급 기능 · manuscript/chapters/14-modules-packages.md:249]
# module_info.py
import cafe_utils

# 모듈 정보 확인
print(f"모듈명: {cafe_utils.__name__}")
print(f"파일 경로: {cafe_utils.__file__}")
print(f"모듈 문서: {cafe_utils.__doc__}")

# 모듈에 정의된 모든 이름 확인
print("모듈의 모든 속성:")
for name in dir(cafe_utils):
    if not name.startswith('_'):  # private 속성 제외
        obj = getattr(cafe_utils, name)
        print(f"  {name}: {type(obj).__name__}")
