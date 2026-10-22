# [1권 Chapter 1. 파이썬 첫 걸음 · 1.3 첫 번째 파이썬 프로그램 · manuscript/chapters/01-python-first-steps.md:280]
# korean_greeting.py
import datetime

def 한국어_인사():
    현재시간 = datetime.datetime.now()
    
    if 현재시간.hour < 12:
        인사말 = "좋은 아침입니다"
    elif 현재시간.hour < 18:
        인사말 = "안녕하세요"
    else:
        인사말 = "안녕하세요, 수고하셨습니다"
    
    return f"{인사말}! 오늘은 {현재시간.strftime('%Y년 %m월 %d일')}입니다."

# 함수 실행
메시지 = 한국어_인사()
print(메시지)
