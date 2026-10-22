# [2권 Chapter 21. 종합 프로젝트: 맛집 추천 AI · 21.2 예제용 데이터 만들기 · manuscript-vol2/chapters/21-capstone-recommender.md:271]
import numpy as np

from 맛집데이터 import 데이터_만들기

데이터 = 데이터_만들기(씨앗=0)
식당, 사용자, 방문 = 데이터.식당, 데이터.사용자, 데이터.방문
print(f"식당 {len(식당)}곳, 사용자 {len(사용자):,}명, 방문 {len(방문):,}번")

보이는_열 = [열 for 열 in 식당.columns if not 열.startswith("숨은_")]
print(식당[보이는_열].head(3).to_string(index=False))
print(방문.head(3).to_string(index=False))

방문수 = 방문.groupby("사용자").size()
print(f"사용자 한 명의 방문: 중앙값 {방문수.median():.0f}번, 가장 많은 사람 {방문수.max()}번")
식당별 = 방문["식당"].value_counts()
print(f"방문이 가장 많은 식당 10%가 받은 방문: {식당별.head(len(식당) // 10).sum() / len(방문):.1%}")
print(f"다시 간 방문의 비율: {방문.duplicated(['사용자', '식당']).mean():.1%}")
print("평점 분포:", 방문["평점"].value_counts().sort_index().to_dict())
채워진_칸 = 방문[["사용자", "식당"]].drop_duplicates().shape[0]
print(f"사용자 × 식당 표에서 채워진 칸: {채워진_칸:,} / {len(사용자) * len(식당):,} "
      f"= {채워진_칸 / (len(사용자) * len(식당)):.2%}")
