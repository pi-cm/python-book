# [2권 Chapter 13. 한국어 NLP 실전: 토크나이저부터 감성 분류까지 · 13.1 이 장의 데이터: 네이버 영화 리뷰 · manuscript-vol2/chapters/13-korean-nlp.md:93]
from 한국어도구 import NSMC_읽기

학습 = NSMC_읽기("ratings_train.txt")
시험 = NSMC_읽기("ratings_test.txt")
print(f"학습 {len(학습):,}개, 시험 {len(시험):,}개")
print(f"긍정(1) 비율: 학습 {sum(y for _, y in 학습) / len(학습):.3f}, "
      f"시험 {sum(y for _, y in 시험) / len(시험):.3f}")

# 원문 대신 리뷰가 어떤 모습인지 세어 본다
문장들 = [문장 for 문장, _ in 학습]
for 이름, 조건 in [("띄어쓰기가 하나도 없음", lambda s: " " not in s),
                   ("'ㅋ'나 'ㅎ'가 들어 있음", lambda s: "ㅋ" in s or "ㅎ" in s),
                   ("마침표를 두 개 이상 이어 씀", lambda s: ".." in s),
                   ("영어 알파벳이 들어 있음", lambda s: any("a" <= c.lower() <= "z" for c in s))]:
    print(f"{이름}: {sum(map(조건, 문장들)) / len(문장들):.1%}")

길이 = sorted(len(문장) for 문장, _ in 학습)
print("글자 수: 중앙값", 길이[len(길이) // 2], "/ 90% 지점", 길이[int(len(길이) * 0.9)],
      "/ 가장 긴 것", 길이[-1])
