# [2권 Chapter 1. 머신러닝이란: 규칙을 짜지 않고 데이터로 배우기 · 1.11 딥러닝은 무엇이 다른가요? · manuscript-vol2/chapters/01-what-is-ml.md:998]
from sklearn.datasets import load_digits

숫자 = load_digits()
print("이미지 모양:", 숫자.images.shape, " 특성 모양:", 숫자.data.shape)
print("픽셀 값 범위:", 숫자.data.min(), "~", 숫자.data.max())

그림 = 숫자.images[0]                  # 8 × 8 픽셀, 0(흰색)~16(검은색)
for 줄 in 그림:
    print("".join(" .:-=+*#%@"[int(값) * 9 // 16] * 2 for 값 in 줄))
print("레이블:", 숫자.target[0])
