"""1권 Chapter 17: 표준 라이브러리 핵심 가이드 — 수학과 통계

원고: manuscript/chapters/17-standard-library-guide.md (561줄부터)
"""

# ---- 원고 561줄 ----
import math
import decimal
from decimal import Decimal

# 한국 주식 계산 (소수점 정밀도 중요)
decimal.getcontext().prec = 10

stock_price = Decimal('45600')  # 삼성전자 주가
shares = 100
commission_rate = Decimal('0.00015')  # 0.015% 수수료

# 매수 총액 계산
total_cost = stock_price * shares
commission = total_cost * commission_rate
final_cost = total_cost + commission

print(f"주가: {stock_price:,}원")
print(f"주식 수: {shares}주")
print(f"매수 총액: {total_cost:,}원")
print(f"수수료: {commission:.0f}원")
print(f"최종 비용: {final_cost:,.0f}원")

# 복리 계산 (적금, 예금)
def compound_interest(principal, rate, years, compounds_per_year=12):
    """복리 이자 계산"""
    amount = principal * (1 + rate / compounds_per_year) ** (compounds_per_year * years)
    return amount

# 월 50만원 적금, 연 3% 이자, 3년
monthly_saving = 500000
annual_rate = 0.03
years = 3

total_principal = monthly_saving * 12 * years
final_amount = sum(
    compound_interest(monthly_saving, annual_rate, (36 - month) / 12, 12)
    for month in range(36)
)

print(f"\n적금 계산:")
print(f"월 납입액: {monthly_saving:,}원")
print(f"총 납입액: {total_principal:,}원")
print(f"만기 수령액: {final_amount:,.0f}원")
print(f"이자 수익: {final_amount - total_principal:,.0f}원")

# ---- 원고 614줄 ----
import statistics

# 한국 주요 도시 인구 데이터 (만 명)
city_populations = [
    ("서울", 972.1),
    ("부산", 341.4),
    ("인천", 246.6),
    ("대구", 153.8),
    ("대전", 150.2),
    ("광주", 103.5),
    ("울산", 103.4),
    ("수원", 119.5),
    ("창원", 104.0)
]

populations = [pop for city, pop in city_populations]

# 기본 통계
print("한국 주요 도시 인구 통계 (단위: 만 명)")
print(f"평균: {statistics.mean(populations):.1f}")
print(f"중앙값: {statistics.median(populations):.1f}")
print(f"최빈값: 없음 (모든 값이 다름)")
print(f"표준편차: {statistics.stdev(populations):.1f}")
print(f"분산: {statistics.variance(populations):.1f}")

# 사분위수
sorted_pops = sorted(populations)
q1 = statistics.quantiles(sorted_pops, n=4)[0]
q3 = statistics.quantiles(sorted_pops, n=4)[2]
print(f"1사분위수: {q1:.1f}")
print(f"3사분위수: {q3:.1f}")
print(f"사분위수 범위: {q3 - q1:.1f}")

# 회사 직원 연봉 분석
salaries = [3200, 3500, 3800, 4200, 4500, 4800, 5200, 5500, 6000, 7500]  # 만원

print(f"\n직원 연봉 통계 (단위: 만원)")
print(f"평균 연봉: {statistics.mean(salaries):,.0f}")
print(f"중간 연봉: {statistics.median(salaries):,.0f}")
print(f"연봉 표준편차: {statistics.stdev(salaries):.0f}")
