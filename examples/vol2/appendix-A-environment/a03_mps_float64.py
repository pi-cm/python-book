# [2권 부록 A. 실행 환경 만들기 · A.7 자주 만나는 설치 문제 · manuscript-vol2/appendix/A-environment.md:345]
import numpy as np
import torch

배열 = np.array([0.1, 0.2, 0.3])             # NumPy의 기본 실수 자료형은 float64
t = torch.from_numpy(배열)
print("자료형:", t.dtype)

if torch.backends.mps.is_available():
    try:
        t.to("mps")
    except TypeError as 오류:
        print("오류:", 오류)
    print("고친 뒤:", t.float().to("mps").dtype)  # float32로 바꾼 다음 옮긴다
