# [2권 Chapter 2. 데이터 준비: 모델에 넣기 전에 할 일 · 2.1 먼저 데이터를 살펴보기 · manuscript-vol2/chapters/02-data-preparation.md:68]
import numpy as np
import pandas as pd

# 설문으로 모은 회원 기록 (예제용으로 만든 데이터)
회원 = pd.DataFrame({
    "회원번호": [101, 102, 103, 104, 105, 106, 107, 107, 108, 109],
    "나이": [27, 999, 45, np.nan, 38, 0, 52, 52, 31, 44],
    "지역": ["서울", "서울시", "부산", "서울 ", "대구", "부산", "서울", "서울", None, "대구"],
    "가입일": ["2025-01-03", "2025-01-10", "2025-02-01", "2025-02-14", "2025-03-02",
               "2025-03-09", "2025-03-20", "2025-03-20", "2025-04-01", "2025-04-11"],
    "탈퇴": [0, 0, 1, 0, 0, 0, 1, 1, 0, 0],
})

print("모양:", 회원.shape)
print("자료형:", dict(회원.dtypes.astype(str)))
print("빈칸 수:", dict(zip(회원.columns, 회원.isna().sum().tolist())))
print("중복 행:", 회원.duplicated().sum(), "개")
print("지역 값:", 회원["지역"].value_counts(dropna=False).to_dict())
print("나이 범위:", 회원["나이"].min(), "~", 회원["나이"].max())
print("정답 비율:", 회원["탈퇴"].value_counts(normalize=True).round(2).to_dict())
