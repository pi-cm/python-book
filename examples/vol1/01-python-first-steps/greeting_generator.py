# [1권 Chapter 1. 파이썬 첫 걸음 · 실습 프로젝트: 나만의 인사말 생성기 · manuscript/chapters/01-python-first-steps.md:334]
# greeting_generator.py
import datetime
from typing import Optional

def 인사말_생성기():
    """개인 맞춤형 인사말을 생성하는 함수"""
    
    # 사용자 정보 입력
    이름 = input("이름을 입력하세요: ")
    try:
        나이 = int(input("나이를 입력하세요: "))
    except ValueError:
        나이 = 0
    
    # 현재 시간 정보
    현재시간 = datetime.datetime.now()
    시간 = 현재시간.hour
    
    # 시간대별 인사말
    if 시간 < 6:
        기본인사 = "늦은 밤"
    elif 시간 < 12:
        기본인사 = "좋은 아침"
    elif 시간 < 18:
        기본인사 = "좋은 오후"
    else:
        기본인사 = "좋은 저녁"
    
    # 나이에 따른 존댓말 조절
    if 나이 >= 60:
        존댓말 = f"{이름} 어르신"
        인사말 = f"{기본인사}입니다"
    elif 나이 >= 20:
        존댓말 = f"{이름}님"
        인사말 = f"{기본인사}입니다"
    else:
        존댓말 = f"{이름}아" if 이름 else "친구"
        인사말 = f"{기본인사}이야"
    
    # 특별한 날짜 확인 (예: 새해)
    특별메시지 = ""
    if 현재시간.month == 1 and 현재시간.day == 1:
        특별메시지 = " 새해 복 많이 받으세요!"
    elif 현재시간.month == 12 and 현재시간.day == 25:
        특별메시지 = " 메리 크리스마스!"
    
    # 최종 메시지 조합
    최종메시지 = f"{존댓말}, {인사말}!{특별메시지}"
    
    return 최종메시지

# 프로그램 실행
if __name__ == "__main__":
    print("=== 개인 맞춤형 인사말 생성기 ===")
    결과 = 인사말_생성기()
    print(f"\n{결과}")
