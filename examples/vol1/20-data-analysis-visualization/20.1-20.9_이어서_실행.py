"""1권 Chapter 20: 데이터 분석과 시각화 — 20.1 NumPy 기초와 배열 연산 ~ 20.9 데이터 내보내기와 보고서 생성 (앞 절의 정의를 이어 쓰므로 한 파일로 묶음)

원고: manuscript/chapters/20-data-analysis-visualization.md (35줄부터)
"""

# ---- 원고 35줄 ----
import numpy as np

population_list = [967, 342, 243, 295, 146, 147, 114]
population = np.array(population_list)

print(population_list * 2)   # 리스트: 이어 붙이기
print(population * 2)        # 배열: 원소마다 곱하기
print(population > 200)      # 원소마다 비교
print(population[population > 200])

# ---- 원고 60줄 ----
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 한국 주식 종목 수익률 데이터 생성 (예시)
stocks = ['삼성전자', 'SK하이닉스', 'NAVER', '카카오', 'LG화학']
returns = np.array([0.12, -0.05, 0.23, 0.08, 0.15])

print(f"주식 종목: {stocks}")
print(f"수익률: {returns}")
print(f"평균 수익률: {returns.mean():.3f}")

# ---- 원고 83줄 ----
# 다양한 방법으로 배열 생성
zeros_array = np.zeros((3, 4))  # 3x4 영행렬
ones_array = np.ones((2, 3))    # 2x3 일행렬
range_array = np.arange(0, 100, 10)  # 0부터 90까지 10씩 증가

# 한국 인구 데이터 (단위: 만명)
cities = ['서울', '부산', '대구', '인천', '광주', '대전', '울산']
population = np.array([967, 342, 243, 295, 146, 147, 114])

# 배열 연산
total_population = population.sum()
avg_population = population.mean()
max_city_idx = population.argmax()

print(f"총 인구: {total_population}만명")
print(f"평균 인구: {avg_population:.1f}만명")
print(f"최대 인구 도시: {cities[max_city_idx]} ({population[max_city_idx]}만명)")

# ---- 원고 115줄 ----
# 한국 기업 매출 데이터 생성
companies_data = {
    '회사명': ['삼성전자', 'SK하이닉스', 'LG전자', '현대자동차', 'POSCO', 'NAVER', '카카오', 'KB금융'],
    '업종': ['전자', '반도체', '전자', '자동차', '철강', 'IT서비스', 'IT서비스', '금융'],
    '매출액': [279102, 44068, 63261, 117611, 64520, 5587, 6706, 12345],  # 단위: 억원
    '영업이익': [35994, 8894, 1543, 4527, 1837, 1646, 645, 3210],
    '직원수': [104756, 24549, 52686, 120565, 19049, 3060, 4446, 12543],
    '설립년도': [1969, 1983, 1958, 1967, 1968, 1999, 1995, 2008]
}

df = pd.DataFrame(companies_data)
print("한국 주요 기업 데이터:")
print(df.head())

# ---- 원고 137줄 ----
# 데이터프레임 기본 정보
print("데이터 기본 정보:")
print(df.info())
print("\n기술통계:")
print(df.describe())

# 영업이익률 계산
df['영업이익률'] = (df['영업이익'] / df['매출액'] * 100).round(2)
print("\n영업이익률이 추가된 데이터:")
print(df[['회사명', '매출액', '영업이익', '영업이익률']])

# ---- 원고 173줄 ----
# 결측치가 포함된 고객 데이터 생성
customer_data = {
    '고객ID': [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008],
    '나이': [25, np.nan, 35, 42, np.nan, 28, 33, 45],
    '소득': [3500, 4200, np.nan, 5800, 3200, np.nan, 4500, 6200],
    '지역': ['서울', '부산', '대구', np.nan, '인천', '광주', '대전', '서울'],
    '구매금액': [120, 0, 85, 250, np.nan, 95, 180, 320]
}

customers_df = pd.DataFrame(customer_data)
print("결측치가 포함된 고객 데이터:")
print(customers_df)

# 결측치 확인
print("\n결측치 현황:")
print(customers_df.isnull().sum())

# 결측치 처리
customers_cleaned = customers_df.copy()
customers_cleaned['나이'] = customers_cleaned['나이'].fillna(customers_cleaned['나이'].mean())
customers_cleaned['소득'] = customers_cleaned['소득'].fillna(customers_cleaned['소득'].mean())
customers_cleaned['지역'] = customers_cleaned['지역'].fillna(customers_cleaned['지역'].mode()[0])
customers_cleaned['구매금액'] = customers_cleaned['구매금액'].fillna(0)

print("\n결측치 처리 후:")
print(customers_cleaned)

# ---- 원고 226줄 ----
# 한국 부동산 매매 데이터 (가상)
np.random.seed(42)
real_estate_data = {
    '지역': ['강남구', '서초구', '송파구', '영등포구', '마포구', '용산구', '강동구', '성북구'] * 12,
    '매매가': np.random.normal(80000, 30000, 96),  # 만원 단위
    '면적': np.random.normal(84, 25, 96),  # 제곱미터
    '층수': np.random.randint(1, 20, 96),
    '건축년도': np.random.randint(1990, 2024, 96),
    '월': np.repeat(range(1, 13), 8)
}

real_estate_df = pd.DataFrame(real_estate_data)
real_estate_df['매매가'] = real_estate_df['매매가'].clip(lower=20000)  # 2억 원 미만은 2억 원으로
real_estate_df['면적'] = real_estate_df['면적'].clip(lower=20)  # 20㎡ 미만은 20㎡로

print("부동산 매매 데이터 요약:")
print(real_estate_df.describe())

# 지역별 평균 매매가
region_stats = real_estate_df.groupby('지역').agg({
    '매매가': ['mean', 'median', 'std', 'count'],
    '면적': 'mean'
}).round(2)

print("\n지역별 부동산 통계:")
print(region_stats)

# ---- 원고 280줄 ----
import platform

# 운영체제별 기본 한글 글꼴 (리눅스·Colab은 나눔글꼴을 먼저 설치)
korean_fonts = {'Darwin': 'AppleGothic', 'Windows': 'Malgun Gothic'}
plt.rcParams['font.family'] = korean_fonts.get(platform.system(), 'NanumGothic')
plt.rcParams['axes.unicode_minus'] = False

# 그림 크기 설정
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# 1. 지역별 평균 매매가 막대 그래프
region_avg_price = real_estate_df.groupby('지역')['매매가'].mean().sort_values(ascending=False)
axes[0, 0].bar(region_avg_price.index, region_avg_price.values)
axes[0, 0].set_title('지역별 평균 매매가')
axes[0, 0].set_ylabel('매매가 (만원)')
axes[0, 0].tick_params(axis='x', rotation=45)

# 2. 면적과 매매가 산점도
axes[0, 1].scatter(real_estate_df['면적'], real_estate_df['매매가'], alpha=0.6)
axes[0, 1].set_title('면적 vs 매매가')
axes[0, 1].set_xlabel('면적 (㎡)')
axes[0, 1].set_ylabel('매매가 (만원)')

# 3. 매매가 분포 히스토그램
sns.histplot(real_estate_df['매매가'], bins=20, color='skyblue', ax=axes[1, 0])
axes[1, 0].set_title('매매가 분포')
axes[1, 0].set_xlabel('매매가 (만원)')
axes[1, 0].set_ylabel('빈도')

# 4. 월별 매매 건수 선그래프
monthly_counts = real_estate_df.groupby('월').size()
axes[1, 1].plot(monthly_counts.index, monthly_counts.values, marker='o')
axes[1, 1].set_title('월별 매매 건수')
axes[1, 1].set_xlabel('월')
axes[1, 1].set_ylabel('매매 건수')
axes[1, 1].set_xticks(range(1, 13))

plt.tight_layout()
plt.show()

# ---- 원고 324줄 ----
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'AppleGothic'   # macOS 기본 한글 글꼴
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots()
ax.bar(['서울', '부산', '대구'], [967, 342, 243])
ax.set_title('도시별 인구 (만 명)')
fig.savefig('population.png', dpi=150)
print('저장 완료')

# ---- 원고 359줄 ----
# 온라인 쇼핑몰 주문 데이터 생성
np.random.seed(123)
order_data = {
    '주문ID': range(1, 1001),
    '고객ID': np.random.randint(1001, 1201, 1000),
    '상품카테고리': np.random.choice(['전자제품', '의류', '식품', '화장품', '도서'], 1000),
    '주문금액': np.random.lognormal(mean=10, sigma=0.5, size=1000).astype(int),
    '주문일': pd.date_range('2024-01-01', periods=1000, freq='h')[:1000],
    '배송지역': np.random.choice(['서울', '경기', '부산', '대구', '인천', '광주', '대전'], 1000)
}

orders_df = pd.DataFrame(order_data)
orders_df['주문월'] = orders_df['주문일'].dt.month

print("주문 데이터 샘플:")
print(orders_df.head())

# 카테고리별 매출 분석
category_sales = orders_df.groupby('상품카테고리').agg({
    '주문금액': ['sum', 'mean', 'count', 'std'],
    '고객ID': 'nunique'
}).round(2)

category_sales.columns = ['총매출', '평균주문액', '주문건수', '주문액표준편차', '고객수']
category_sales['객단가'] = (category_sales['총매출'] / category_sales['고객수']).round(0)

print("\n카테고리별 매출 분석:")
print(category_sales.sort_values('총매출', ascending=False))

# ---- 원고 411줄 ----
# 주식 가격 데이터 생성 (가상의 삼성전자 주가)
date_range = pd.date_range('2023-01-01', '2024-12-31', freq='D')
np.random.seed(42)

# 주가 시뮬레이션 (랜덤워크 + 트렌드)
price_changes = np.random.normal(0, 2, len(date_range))
trend = np.linspace(0, 5000, len(date_range))  # 2년간 5000원 오르는 상승 트렌드
prices = 70000 + np.cumsum(price_changes) + trend + np.random.normal(0, 500, len(date_range))

stock_data = pd.DataFrame({
    '날짜': date_range,
    '종가': prices.astype(int),
    '거래량': np.random.lognormal(mean=15, sigma=0.3, size=len(date_range)).astype(int)
})

# 주말 제거 (실제 거래일만)
stock_data = stock_data[stock_data['날짜'].dt.weekday < 5]
stock_data = stock_data.reset_index(drop=True)

print("주식 데이터 샘플:")
print(stock_data.head(10))

# 시계열 특성 추가
stock_data['년도'] = stock_data['날짜'].dt.year
stock_data['월'] = stock_data['날짜'].dt.month
stock_data['일일수익률'] = stock_data['종가'].pct_change() * 100

# 이동평균 계산
stock_data['MA_5'] = stock_data['종가'].rolling(window=5).mean()
stock_data['MA_20'] = stock_data['종가'].rolling(window=20).mean()
stock_data['MA_60'] = stock_data['종가'].rolling(window=60).mean()

print("\n이동평균이 추가된 데이터:")
print(stock_data[['날짜', '종가', 'MA_5', 'MA_20', 'MA_60']].tail())

# ---- 원고 466줄 ----
# 더 현실적인 온라인 쇼핑몰 데이터 생성
np.random.seed(123)

# 고객 마스터 데이터
customers = pd.DataFrame({
    '고객ID': range(1001, 1501),
    '연령': np.random.normal(35, 12, 500).astype(int).clip(18, 70),
    '성별': np.random.choice(['남성', '여성'], 500),
    '거주지역': np.random.choice(['서울', '경기', '부산', '대구', '인천', '광주', '대전', '울산'], 500, 
                               p=[0.25, 0.2, 0.15, 0.1, 0.1, 0.08, 0.07, 0.05]),
    '가입일': pd.date_range('2020-01-01', periods=500, freq='D')[:500]
})

# 상품 마스터 데이터
products = pd.DataFrame({
    '상품ID': range(2001, 2051),
    '상품명': [f'상품_{i}' for i in range(2001, 2051)],
    '카테고리': np.random.choice(['전자제품', '패션', '화장품', '식품', '도서', '스포츠'], 50),
    '브랜드': np.random.choice(['브랜드A', '브랜드B', '브랜드C', '브랜드D', '브랜드E'], 50),
    '정가': np.random.lognormal(mean=9, sigma=0.5, size=50).astype(int)
})

# 주문 데이터 생성
order_count = 5000
orders = pd.DataFrame({
    '주문ID': range(3001, 3001 + order_count),
    '고객ID': np.random.choice(customers['고객ID'], order_count),
    '상품ID': np.random.choice(products['상품ID'], order_count),
    '주문일시': pd.date_range('2023-01-01', periods=order_count, freq='h')[:order_count],
    '수량': np.random.choice([1, 2, 3, 4, 5], order_count, p=[0.6, 0.2, 0.1, 0.07, 0.03])
})

# 데이터 결합
orders_merged = orders.merge(customers, on='고객ID').merge(products, on='상품ID')
orders_merged['주문금액'] = orders_merged['정가'] * orders_merged['수량']

print("종합 주문 데이터 구조:")
print(orders_merged.head())
print(f"\n데이터 크기: {orders_merged.shape}")

# ---- 원고 526줄 ----
# 1. 매출 현황 분석
print("=== 1. 매출 현황 분석 ===")
total_revenue = orders_merged['주문금액'].sum()
total_orders = len(orders_merged)
avg_order_value = orders_merged['주문금액'].mean()
unique_customers = orders_merged['고객ID'].nunique()

print(f"총 매출: {total_revenue:,.0f}원")
print(f"총 주문건수: {total_orders:,}건")
print(f"평균 주문가: {avg_order_value:,.0f}원")
print(f"고유 고객수: {unique_customers:,}명")
print(f"고객당 평균 주문가: {total_revenue/unique_customers:,.0f}원")

# 2. 카테고리별 성과 분석
print("\n=== 2. 카테고리별 성과 분석 ===")
category_performance = orders_merged.groupby('카테고리').agg({
    '주문금액': ['sum', 'mean', 'count'],
    '고객ID': 'nunique',
    '수량': 'sum'
}).round(0)

category_performance.columns = ['총매출', '평균주문가', '주문건수', '고객수', '총판매량']
category_performance['시장점유율'] = (category_performance['총매출'] / total_revenue * 100).round(1)
category_performance = category_performance.sort_values('총매출', ascending=False)

print(category_performance)

# 3. 고객 세그멘테이션
print("\n=== 3. 고객 세그멘테이션 ===")
customer_rfm = orders_merged.groupby('고객ID').agg({
    '주문일시': 'max',
    '주문금액': ['sum', 'count']
}).reset_index()

customer_rfm.columns = ['고객ID', '최근구매일', '총구매금액', '구매빈도']
customer_rfm['최근성'] = (pd.Timestamp('2024-01-01') - customer_rfm['최근구매일']).dt.days

# RFM 점수 계산 (1-5점)
customer_rfm['R_Score'] = pd.qcut(customer_rfm['최근성'], 5, labels=[5,4,3,2,1])
customer_rfm['F_Score'] = pd.qcut(customer_rfm['구매빈도'].rank(method='first'), 5, labels=[1,2,3,4,5])
customer_rfm['M_Score'] = pd.qcut(customer_rfm['총구매금액'], 5, labels=[1,2,3,4,5])

# 고객 등급 정의
def customer_segment(row):
    if row['R_Score'] >= 4 and row['F_Score'] >= 4 and row['M_Score'] >= 4:
        return 'Champions'
    elif row['R_Score'] >= 3 and row['F_Score'] >= 3 and row['M_Score'] >= 3:
        return 'Loyal Customers'
    elif row['R_Score'] >= 4:
        return 'New Customers'
    elif row['M_Score'] >= 4:
        return 'Big Spenders'
    elif row['R_Score'] <= 2:
        return 'At Risk'
    else:
        return 'Others'

customer_rfm['고객등급'] = customer_rfm.apply(customer_segment, axis=1)

segment_summary = customer_rfm.groupby('고객등급').agg({
    '고객ID': 'count',
    '총구매금액': 'mean',
    '구매빈도': 'mean',
    '최근성': 'mean'
}).round(1)

segment_summary.columns = ['고객수', '평균구매금액', '평균구매빈도', '평균최근성']
print(segment_summary)

# ---- 원고 622줄 ----
# 분석 결과를 다양한 형식으로 저장
import os

# 결과 저장용 디렉토리 생성
os.makedirs('analysis_results', exist_ok=True)

# 1. CSV 파일로 저장
category_performance.to_csv('analysis_results/category_analysis.csv', encoding='utf-8-sig')
customer_rfm.to_csv('analysis_results/customer_segmentation.csv', encoding='utf-8-sig', index=False)

# 2. Excel 파일로 저장 (여러 시트)
with pd.ExcelWriter('analysis_results/comprehensive_analysis.xlsx') as writer:
    category_performance.to_excel(writer, sheet_name='카테고리_분석')
    segment_summary.to_excel(writer, sheet_name='고객_세그먼트')
    orders_merged.head(100).to_excel(writer, sheet_name='주문_데이터_샘플', index=False)

# 3. JSON 형식으로 저장
analysis_summary = {
    '분석_일자': '2024-01-01',
    '총매출': int(total_revenue),
    '총주문건수': total_orders,
    '평균주문가': int(avg_order_value),
    '고유고객수': unique_customers,
    '주요_카테고리': category_performance.head(3).to_dict('index'),
    '고객_세그먼트_분포': segment_summary.to_dict('index')
}

import json
with open('analysis_results/analysis_summary.json', 'w', encoding='utf-8') as f:
    json.dump(analysis_summary, f, ensure_ascii=False, indent=2)

print("분석 결과가 다음 파일들로 저장되었습니다:")
print("- analysis_results/category_analysis.csv")
print("- analysis_results/customer_segmentation.csv") 
print("- analysis_results/comprehensive_analysis.xlsx")
print("- analysis_results/analysis_summary.json")
