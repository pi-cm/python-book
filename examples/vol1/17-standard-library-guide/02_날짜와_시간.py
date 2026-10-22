"""1권 Chapter 17: 표준 라이브러리 핵심 가이드 — 날짜와 시간

원고: manuscript/chapters/17-standard-library-guide.md (139줄부터)
"""

# ---- 원고 139줄 ----
import datetime
from zoneinfo import ZoneInfo

# 한국 시간 다루기
seoul_tz = ZoneInfo("Asia/Seoul")
now_seoul = datetime.datetime.now(seoul_tz)
print(f"현재 서울 시간: {now_seoul.strftime('%Y년 %m월 %d일 %H시 %M분')}")

# UTC와 한국시간 변환
utc_time = datetime.datetime.now(datetime.timezone.utc)
seoul_time = utc_time.astimezone(seoul_tz)
print(f"UTC: {utc_time}")
print(f"서울: {seoul_time}")

# 한국 날짜 형식
korean_format = now_seoul.strftime('%Y년 %m월 %d일 (%a)')
print(f"한국식 날짜: {korean_format}")

# 업무일 계산 (주말 제외)
def add_business_days(start_date, days):
    current = start_date
    while days > 0:
        current += datetime.timedelta(days=1)
        if current.weekday() < 5:  # 월-금 (0-4)
            days -= 1
    return current

start = datetime.date.today()
business_day = add_business_days(start, 5)
print(f"5영업일 후: {business_day}")

# ---- 원고 184줄 ----
import calendar

# 한국어 달력 생성
calendar.setfirstweekday(calendar.SUNDAY)  # 일요일부터 시작

# 2024년 3월 달력
march_2024 = calendar.month(2024, 3)
print("2024년 3월:")
print(march_2024)

# 특정 날짜가 무슨 요일인지
day_of_week = calendar.weekday(2024, 3, 1)
korean_days = ['월', '화', '수', '목', '금', '토', '일']
print(f"2024년 3월 1일은 {korean_days[day_of_week]}요일")

# 한국 공휴일 데이터
korean_holidays_2024 = {
    (1, 1): "신정",
    (2, 9): "설날 연휴",
    (2, 10): "설날",
    (2, 11): "설날 연휴",
    (2, 12): "설날 대체공휴일",
    (3, 1): "삼일절",
    (4, 10): "국회의원 선거일",
    (5, 5): "어린이날",
    (5, 6): "어린이날 대체공휴일",
    (5, 15): "부처님 오신날",
    (6, 6): "현충일",
    (8, 15): "광복절",
    (9, 16): "추석 연휴",
    (9, 17): "추석",
    (9, 18): "추석 연휴",
    (10, 1): "국군의 날(임시공휴일)",
    (10, 3): "개천절",
    (10, 9): "한글날",
    (12, 25): "크리스마스"
}

def is_korean_holiday(date):
    return (date.month, date.day) in korean_holidays_2024

# ---- 원고 233줄 ----
from datetime import date

import holidays

kr_holidays = holidays.KR(years=2024, language="ko")
for day, name in sorted(kr_holidays.items()):
    if day.month == 9:
        print(day, name)

print(date(2024, 9, 19) in kr_holidays)  # 추석 연휴가 끝난 다음 날
print(date(2024, 10, 1) in kr_holidays)  # 국군의 날 임시공휴일
