# Chapter 20: 데이터 분석과 시각화

> **학습 목표**  
> - NumPy 배열과 pandas 데이터프레임 다루기
> - 결측치와 이상값을 정리하고 탐색적 분석하기
> - matplotlib로 한글이 깨지지 않는 그래프 그리기
> - 그룹 집계와 시계열 분석으로 데이터에서 이야기 찾기

---

## 들어가며: 숫자 더미에서 이야기를 꺼내려면?

한 달 치 카드 사용 내역을 내려받았다고 해 봅시다. 300줄쯤 되는 표예요. 그런데 "이번 달엔 왜 이렇게 많이 썼지?"라는 질문에 답하려면 300줄을 위에서부터 읽어 내려가야 할까요?

아마 이렇게 할 겁니다. 먼저 이상한 줄(금액이 비어 있거나, 같은 결제가 두 번 찍힌 줄)을 정리하고, 식비·교통비·쇼핑처럼 **묶은 다음**, 묶음마다 **합계를 내고**, 마지막으로 막대그래프를 그려서 **한눈에 봅니다**. 그러면 "아, 배달 음식이 지난달보다 두 배구나" 하는 이야기가 보이죠.

데이터 분석이 하는 일이 바로 이겁니다. **정리하고, 묶고, 요약하고, 그림으로 본다.** 이 장에서는 이 네 단계를 파이썬으로 해 봅니다. 도구는 세 가지예요.

- **NumPy**: 숫자를 한꺼번에 계산하는 계산기. 숫자 수천 개에 한 번에 2를 곱할 수 있습니다.
- **pandas**: 파이썬 속의 엑셀. 이름 붙은 열과 행으로 이루어진 표(데이터프레임)를 다룹니다.
- **matplotlib**(와 그 위에 얹은 seaborn): 표를 그림으로 바꿔 주는 화가.

셋 다 표준 라이브러리가 아니라서 먼저 설치해야 합니다. 프로젝트 폴더에서 `uv add numpy pandas matplotlib seaborn`을 실행하세요. 20.9절의 엑셀 저장까지 따라 하려면 `openpyxl`도 함께 설치해야 합니다. pandas가 엑셀 파일을 쓸 때 이 패키지를 빌려 쓰거든요. 설치하지 않고 엑셀로 저장하려고 하면 `ModuleNotFoundError: No module named 'openpyxl'`이 납니다.

이 장의 예제 데이터는 모두 연습용으로 지어낸 값입니다. 회사 매출이나 주가처럼 보여도 실제 수치가 아니니, 숫자 자체보다 **숫자를 다루는 방법**에 집중해 주세요. 그리고 이 장의 코드는 한 파일에 이어서 실행한다고 생각하고 읽으면 됩니다. 앞 절에서 만든 `np`, `pd`, `real_estate_df` 같은 이름을 뒤에서 그대로 씁니다.

## 20.1 NumPy 기초와 배열 연산

파이썬 리스트로도 숫자를 담을 수 있는데 왜 NumPy가 따로 필요할까요?

리스트는 무엇이든 담을 수 있는 **잡동사니 상자**입니다. 숫자, 문자열, 다른 리스트까지 섞어 넣을 수 있죠. 대신 "안에 든 숫자에 모두 2를 곱해 줘" 같은 일은 못 합니다. 반복문을 돌면서 하나씩 꺼내 곱해야 해요. NumPy 배열은 반대로 **같은 종류의 숫자만 줄 맞춰 담는 계란판**입니다. 칸마다 같은 크기의 숫자가 들어 있으니, 판 전체에 한 번에 연산을 할 수 있어요.

차이는 `* 2` 한 번으로 바로 보입니다.

```python
import numpy as np

population_list = [967, 342, 243, 295, 146, 147, 114]
population = np.array(population_list)

print(population_list * 2)   # 리스트: 이어 붙이기
print(population * 2)        # 배열: 원소마다 곱하기
print(population > 200)      # 원소마다 비교
print(population[population > 200])
```

```text
[967, 342, 243, 295, 146, 147, 114, 967, 342, 243, 295, 146, 147, 114]
[1934  684  486  590  292  294  228]
[ True  True  True  True False False False]
[967 342 243 295]
```

리스트에 `* 2`를 하면 같은 리스트를 두 번 **이어 붙입니다**. 배열에 `* 2`를 하면 칸마다 **곱합니다**. 비교도 마찬가지라 `population > 200`은 칸마다 `True`/`False`를 담은 배열이 되고, 이 배열을 대괄호에 넣으면 `True`인 칸만 골라낼 수 있어요. 이렇게 반복문 없이 배열 전체에 한 번에 연산하는 것을 **벡터화(vectorization)** 라고 부릅니다. 앞으로 나올 pandas의 열 계산도 전부 이 방식이에요.

### NumPy 시작하기

아래 코드는 이 장 전체에서 쓸 네 가지 도구를 한꺼번에 불러옵니다. `np`, `pd`, `plt`, `sns`는 데이터 분석하는 사람들이 거의 약속처럼 쓰는 줄임 이름이라, 다른 사람의 코드를 읽을 때도 그대로 만나게 됩니다.

```python
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
```

`returns.mean()`처럼 평균을 배열이 **스스로** 계산한다는 점을 보세요. 리스트였다면 `sum(returns) / len(returns)`라고 써야 했을 거예요. 결과는 `0.106`, 즉 다섯 종목의 평균 수익률이 10.6%라는 뜻입니다.

### 배열 생성과 조작

배열은 직접 숫자를 적어서 만들 수도 있지만, 모양만 정해 주고 만들 수도 있습니다. `np.zeros((3, 4))`는 0으로 채운 3행 4열짜리 빈 계란판, `np.arange(0, 100, 10)`은 `range()`의 배열 버전이에요.

그다음 도시 인구 예제에서는 `sum()`, `mean()`, `argmax()`를 씁니다. 앞의 둘은 이름 그대로 합계와 평균이고, `argmax()`는 **가장 큰 값 자체가 아니라 그 값이 있는 자리(인덱스)** 를 돌려줍니다. 인덱스를 알면 같은 순서로 만든 `cities` 리스트에서 도시 이름을 꺼낼 수 있죠.

```python
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
```

실행하면 총 인구 2254만 명, 평균 322.0만 명, 최대 인구 도시는 서울(967만 명)이 나옵니다. 그런데 일곱 도시 가운데 평균(322만 명)보다 인구가 많은 곳은 서울과 부산 둘뿐이에요. 서울 하나가 평균을 크게 끌어올렸기 때문입니다. 평균은 이렇게 큰 값 하나에 쉽게 흔들립니다. 이 점은 다음 절에서 다시 만나요.

## 20.2 Pandas 데이터프레임 조작

NumPy 배열은 숫자 계산에는 훌륭하지만, 실제 데이터는 대개 이렇게 생겼습니다. "회사명은 글자, 매출액은 숫자, 설립년도는 연도." 열마다 종류가 다르고, 열마다 이름이 있죠. 엑셀 표처럼요.

pandas는 바로 이런 표를 다루는 라이브러리입니다. 표 전체를 **데이터프레임(DataFrame)**, 표의 열 하나를 **시리즈(Series)** 라고 부릅니다. 시리즈는 "이름표가 붙은 NumPy 배열"이라고 생각하면 돼요. 그래서 앞 절에서 배운 벡터화 계산을 열 단위로 그대로 쓸 수 있습니다.

### 데이터프레임 생성

데이터프레임을 만드는 가장 쉬운 방법은 딕셔너리를 넘기는 것입니다. **키가 열 이름, 값(리스트)이 그 열의 내용**이 됩니다. 리스트 길이는 모두 같아야 해요. 표의 칸이 비면 안 되니까요.

```python
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
```

`head()`는 표의 맨 앞 다섯 줄만 보여 줍니다. 데이터가 수만 줄이어도 생김새를 빠르게 확인할 수 있죠. 출력 맨 왼쪽의 `0, 1, 2, …`는 우리가 넣은 값이 아니라 pandas가 붙인 행 번호, **인덱스**입니다.

### 기본 정보 확인

처음 받은 데이터는 먼저 건강검진부터 합니다. `info()`는 열마다 이름, 비어 있지 않은 값의 개수(Non-Null Count), 자료형을 알려 주고, `describe()`는 숫자 열마다 개수·평균·표준편차·최솟값·사분위수·최댓값을 한 번에 계산해 줍니다.

```python
# 데이터프레임 기본 정보
print("데이터 기본 정보:")
print(df.info())
print("\n기술통계:")
print(df.describe())

# 영업이익률 계산
df['영업이익률'] = (df['영업이익'] / df['매출액'] * 100).round(2)
print("\n영업이익률이 추가된 데이터:")
print(df[['회사명', '매출액', '영업이익', '영업이익률']])
```

결과에서 세 가지를 봐 주세요.

첫째, `print(df.info())`의 마지막 줄에 `None`이 찍힙니다. `info()`는 표를 **직접 화면에 출력하고** 아무것도 돌려주지 않는 함수라서, 그 반환값 `None`을 `print()`가 한 번 더 찍은 거예요. 그냥 `df.info()`라고만 써도 됩니다.

둘째, `describe()`에서 매출액의 평균(mean)은 74150인데 중앙값(50%)은 53664.5입니다. 앞 절의 서울처럼, 매출이 압도적으로 큰 회사 하나가 평균을 끌어올린 거예요. 데이터를 볼 때 평균과 중앙값이 많이 다르면 "한쪽으로 쏠린 값이 있구나" 하고 의심해 보세요.

셋째, `df['영업이익률'] = ...`은 **열 전체를 한 줄로 계산해서 새 열을 만드는** 코드입니다. 반복문이 없죠? 벡터화 덕분입니다. 매출이 가장 큰 회사가 영업이익률까지 가장 높은 것은 아니라는 점도 결과에서 확인할 수 있어요.

> **Q. `df['매출액']`과 `df[['회사명', '매출액']]`은 무엇이 다른가요?**
> 대괄호 안에 열 이름 하나를 넣으면 열 하나, 즉 시리즈가 나옵니다. 열 이름의 **리스트**를 넣으면 그 열들만 골라 담은 작은 데이터프레임이 나와요. 그래서 여러 열을 고를 때는 대괄호가 두 겹이 됩니다. 바깥 대괄호는 "골라 줘", 안쪽 대괄호는 "이 목록대로"라는 뜻입니다.

## 20.3 데이터 클리닝과 전처리

요리를 시작하기 전에 재료를 다듬죠? 시든 잎은 떼고, 흙은 씻어 내고요. 데이터도 똑같습니다. 실제 데이터에는 설문에 답하지 않은 칸, 잘못 입력된 값이 섞여 있어요. 분석가들 사이에는 "분석 시간의 대부분은 데이터 청소에 쓴다"는 말이 있을 정도입니다.

### 결측치 처리

비어 있는 값을 **결측치(missing value)** 라고 하고, pandas에서는 `NaN`(Not a Number)으로 표시합니다. 결측치를 다루는 방법은 크게 두 가지예요. 그 행을 버리거나(`dropna()`), 그럴듯한 값으로 채우거나(`fillna()`). 아래 예제는 채우는 쪽을 택했고, 열의 성격에 따라 채우는 값을 다르게 골랐습니다.

- 나이·소득처럼 **숫자** 열은 평균(`mean()`)으로 채웁니다.
- 지역처럼 **범주** 열은 평균을 낼 수 없으니 가장 많이 나온 값, 최빈값(`mode()`)으로 채웁니다. `mode()`는 최빈값이 여러 개일 수 있어서 시리즈를 돌려주므로 `[0]`으로 첫 번째를 꺼냅니다.
- 구매금액은 "기록이 없으면 사지 않은 것"으로 보고 0으로 채웁니다.

```python
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
```

`isnull().sum()`은 칸마다 비었으면 `True`, 아니면 `False`인 표를 만든 다음 열마다 더합니다. `True`는 1, `False`는 0으로 세니까 결과가 곧 열별 결측치 개수예요. 나이 2개, 소득 2개, 지역 1개, 구매금액 1개가 비어 있습니다.

"결측치 처리 후" 표를 보면 빈 나이 두 칸은 나머지 여섯 명의 평균 34.666667로, 빈 소득 두 칸은 4566.666667로, 빈 지역은 최빈값 '서울'로, 빈 구매금액은 0으로 채워졌습니다.

결측치를 채우는 네 줄이 모두 `열 = 열.fillna(...)`처럼 **고친 열을 다시 대입하는** 모양이라는 점을 눈여겨보세요. 인터넷에서 `customers_cleaned['나이'].fillna(값, inplace=True)`처럼 쓴 코드를 자주 볼 텐데, 최신 pandas(3.0 이후)에서는 이렇게 쓰면 표가 **바뀌지 않습니다**. `customers_cleaned['나이']`로 꺼낸 열은 원본 표와 연결된 열이 아니라 **복사본처럼** 동작하고, `inplace=True`는 그 복사본만 고친 뒤 버리기 때문이에요. pandas 2.2에서는 "앞으로 이 코드는 동작하지 않는다"는 `FutureWarning`이 뜨고, 3.0부터는 `ChainedAssignmentError` 경고와 함께 원본이 그대로 남습니다. 다시 대입하는 방식은 어느 버전에서나 확실하게 동작합니다.

평균으로 채우는 것이 늘 정답은 아니라는 점도 기억해 두세요. 결측치가 많은 열을 평균으로 채우면, 데이터가 실제보다 평균 근처에 몰려 있는 것처럼 보이게 됩니다. 비어 있는 이유가 무엇인지 먼저 생각해 보고, 버릴지 채울지, 무엇으로 채울지를 정하는 게 좋습니다.

## 20.4 탐색적 데이터 분석 (EDA)

처음 이사 간 동네에서는 무엇부터 하나요? 지도를 펴고, 슈퍼는 어디 있는지, 버스 정류장은 어디인지, 밤에 시끄러운 골목은 없는지 한 바퀴 돌아보죠. 무엇을 할지 정하기 전에 **일단 둘러보는 것**입니다.

데이터에서 이 일을 **탐색적 데이터 분석(Exploratory Data Analysis, EDA)** 이라고 합니다. 가설을 세우기 전에 요약 통계를 내 보고, 그룹별로 나눠 보고, 그림을 그려 보면서 데이터가 어떻게 생겼는지 익히는 단계예요.

### 기본 통계 분석

예제에는 처음 보는 함수가 몇 개 나옵니다.

- `np.random.seed(42)`: 난수의 **시작점을 고정**합니다. 컴퓨터가 만드는 난수는 사실 정해진 계산으로 만든 **의사 난수(pseudo-random number)** 라서, 시작점이 같으면 매번 같은 순서로 나옵니다. 그래서 이 책의 결과와 여러분의 결과가 똑같이 나올 수 있어요.
- `np.random.normal(80000, 30000, 96)`: 평균 80000, 표준편차 30000인 **정규분포**(가운데가 볼록한 종 모양)에서 숫자 96개를 뽑습니다.
- `np.random.randint(1, 20, 96)`: 1 이상 20 **미만**의 정수 96개를 뽑습니다. 끝값이 빠지는 것은 `range()`와 같아요.
- `clip(lower=20000)`: 20000보다 작은 값을 모두 20000으로 끌어올립니다. 바닥을 깔아 주는 셈이에요.
- `groupby('지역').agg({...})`: 지역별로 묶은 다음, 열마다 다른 집계를 합니다. 매매가에는 평균·중앙값·표준편차·개수를, 면적에는 평균만 내라는 뜻이에요.

```python
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
```

`describe()` 결과에서 매매가의 최솟값을 보세요. 정확히 20000(2억 원)입니다. 왜 딱 떨어질까요? 정규분포는 평균에서 멀리 떨어진 값도 드물게 뽑아 줍니다. 이 데이터에서도 1407만 원짜리 아파트가 하나 뽑혔어요. 평균 8억짜리 동네에 1400만 원짜리 아파트라니, 현실에는 없는 값이죠. 그래서 `clip(lower=20000)`으로 2억 원 미만을 2억 원으로 끌어올렸고, 그 값이 최솟값으로 보이는 겁니다. 정규분포에서는 0보다 작은 값도 나올 수 있으니, 이런 바닥이 없으면 음수 매매가까지 생길 수 있어요.

EDA에서 최솟값과 최댓값부터 확인하는 이유가 바로 이겁니다. 이런 **이상값(outlier)** 을 찾아내야 버릴지, 고칠지 정할 수 있으니까요. 여기서는 바닥값으로 고치는 쪽을 골랐지만, 실제 데이터라면 그 줄이 입력 실수인지 먼저 확인하고 지우는 편이 나을 때도 많습니다.

지역별 통계 표는 열 이름이 `매매가` 아래에 `mean`, `median`… 이렇게 **두 층**으로 되어 있습니다. 열마다 집계를 여러 개 요청했기 때문이에요. 이 두 층짜리 열 이름은 20.6절에서 한 층으로 정리하는 방법을 봅니다.

## 20.5 Matplotlib과 Seaborn을 활용한 시각화

숫자 96개가 적힌 표와 막대그래프 한 장 중에, 어느 쪽이 "어느 동네가 제일 비싼가?"에 빨리 답해 줄까요? 당연히 그래프죠. 사람의 눈은 숫자를 읽는 것보다 **길이와 위치를 비교하는 것**이 훨씬 빠릅니다.

그래프는 질문에 따라 고릅니다.

| 묻고 싶은 것 | 그래프 | 이 절의 예 |
|---|---|---|
| 항목끼리 크기 비교 | 막대그래프 `bar` | 지역별 평균 매매가 |
| 두 값의 관계 | 산점도 `scatter` | 면적과 매매가 |
| 값이 어떻게 퍼져 있나 | 히스토그램 `hist` | 매매가 분포 |
| 시간에 따른 변화 | 선그래프 `plot` | 월별 매매 건수 |

### 기본 그래프 작성

matplotlib으로 그림을 그릴 때는 **도화지(Figure)** 와 그 위에 붙인 **칸(Axes)** 을 먼저 만듭니다. `plt.subplots(2, 2, figsize=(15, 12))`는 가로 15인치, 세로 12인치 도화지를 2행 2열로 나눠서 칸 네 개를 만들어요. `axes[0, 0]`이 왼쪽 위, `axes[1, 1]`이 오른쪽 아래 칸입니다. 칸마다 그래프를 하나씩 그리고 제목과 축 이름을 붙인 다음, `tight_layout()`으로 칸끼리 글자가 겹치지 않게 간격을 맞추고, `show()`로 화면에 띄웁니다. 세 번째 칸의 히스토그램만은 seaborn의 `sns.histplot()`으로 그렸어요. `ax=axes[1, 0]`으로 그릴 칸을 알려 주면 seaborn도 matplotlib의 칸 위에 그림을 그립니다.

맨 앞부분은 **한글 글꼴** 설정입니다. matplotlib의 기본 글꼴(`DejaVu Sans`)에는 한글 글자 모양이 없어서, 이 설정 없이 그리면 한글 제목과 축 이름이 모두 **네모 상자(□)** 로 나오고 콘솔에는 `Glyph ... missing from font(s) DejaVu Sans` 경고가 줄줄이 찍힙니다. 그래서 운영체제마다 기본으로 들어 있는 한글 글꼴을 고릅니다. `platform.system()`은 macOS에서 `'Darwin'`, 윈도우에서 `'Windows'`를 돌려주니, macOS는 `AppleGothic`, 윈도우는 `Malgun Gothic`(맑은 고딕)을 쓰게 되죠. 리눅스나 Colab에는 기본 한글 글꼴이 없어서 나눔고딕(`NanumGothic`) 같은 글꼴을 먼저 설치해야 합니다. 설치하지 않으면 글꼴을 찾지 못했다는 경고와 함께 다시 네모 상자가 나와요.

```python
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
```

그래프 네 개를 한꺼번에 그리기 전에, 내 컴퓨터에서 한글 글꼴이 제대로 잡히는지 작은 그래프 하나로 먼저 확인해 보면 좋습니다. 아래는 macOS 기준이고, 윈도우라면 `'AppleGothic'` 자리에 `'Malgun Gothic'`을 넣으세요.

```python
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'AppleGothic'   # macOS 기본 한글 글꼴
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots()
ax.bar(['서울', '부산', '대구'], [967, 342, 243])
ax.set_title('도시별 인구 (만 명)')
fig.savefig('population.png', dpi=150)
print('저장 완료')
```

macOS에서 실행하면 경고 없이 `population.png`가 만들어지고, 그림 속 한글도 제대로 보입니다. 글꼴 설정 다음 줄의 `axes.unicode_minus = False`도 짝꿍처럼 따라다니는 설정이에요. matplotlib은 축 눈금의 음수 부호를 일반 하이픈(`-`)이 아니라 수학용 마이너스 기호로 그리는데, 한글 글꼴 중에는 이 기호가 없는 것이 있어서 음수 눈금이 깨질 수 있습니다. `False`로 두면 일반 하이픈을 씁니다.

`plt.show()` 대신 `fig.savefig()`를 쓴 것도 눈여겨보세요. `show()`는 그림을 **창으로 띄우고**, `savefig()`는 **파일로 저장**합니다. 서버나 자동 실행 스크립트처럼 창을 띄울 수 없는 곳에서는 `savefig()`를 써야 해요. 보고서에 그림을 넣을 때도 마찬가지고요. `dpi`는 인치당 점의 개수로, 높을수록 선명하지만 파일이 커집니다.

네 개의 그래프를 다시 보면 이런 이야기가 읽힙니다. 막대그래프에서는 지역별 평균 매매가 차이가 한눈에 보이고, 산점도에서는 면적이 넓다고 매매가가 꼭 높지는 않다는 것(점들이 한 방향으로 늘어서지 않고 흩어져 있죠)이 보입니다. 데이터를 난수로 만들었으니 당연한 결과예요. 실제 데이터라면 점들이 오른쪽 위로 기울어진 띠 모양을 그릴 겁니다. 월별 매매 건수가 일직선인 것도 코드가 매달 8건씩 만들었기 때문이고요. 이렇게 그래프는 데이터에 숨어 있는 **만든 사람의 가정**까지 드러내 줍니다.

> **Q. matplotlib이 있는데 seaborn은 왜 따로 있나요?**
> seaborn은 matplotlib 위에 얹은 라이브러리로, 같은 그래프를 더 적은 코드와 보기 좋은 기본 색으로 그려 줍니다. 예제의 `sns.histplot()`은 막대 테두리를 그려 주고 x축 이름(`매매가`)도 열 이름에서 알아서 붙여요. 예제에서는 그 뒤에 `set_xlabel()`로 단위가 붙은 이름으로 바꿨습니다. seaborn이 그린 그림도 결국 matplotlib의 칸(Axes) 위에 있으니, Figure와 Axes 구조를 먼저 익혀 두면 어느 쪽으로 그린 그림이든 같은 방식으로 다듬을 수 있습니다.

## 20.6 데이터 집계와 그룹화

반 전체 시험 점수가 있을 때 "반 평균"은 숫자 하나지만, "남학생 평균과 여학생 평균", "1분단과 2분단 평균"처럼 **묶어서 비교**하면 훨씬 많은 것이 보입니다. 데이터 분석에서 가장 자주 하는 일이 바로 이 **나누고(split) → 계산하고(apply) → 합치기(combine)** 입니다. pandas에서는 `groupby()` 한 번으로 이 세 단계를 해요.

### GroupBy 연산

이번 예제는 쇼핑몰 주문 1000건을 만들어 카테고리별로 집계합니다. 데이터를 만드는 줄에 새 얼굴이 몇 있어요.

- `np.random.choice([...], 1000)`: 목록에서 하나씩 무작위로 1000번 뽑습니다.
- `np.random.lognormal(mean=10, sigma=0.5, ...)`: **로그정규분포**에서 뽑습니다. 대부분은 적당한 금액이고 가끔 아주 큰 금액이 섞이는, 오른쪽으로 꼬리가 긴 모양이에요. 주문 금액이나 소득처럼 0보다 작을 수 없고 큰 쪽으로 치우친 값을 흉내 낼 때 씁니다.
- `pd.date_range('2024-01-01', periods=1000, freq='h')`: 2024년 1월 1일 0시부터 **1시간 간격**으로 시각 1000개를 만듭니다. 시간 간격 표기는 소문자 `'h'`입니다. 예전 자료에서 보이는 대문자 `'H'`는 pandas 2.2부터 경고가 뜨고, 3.0부터는 `ValueError`가 나요.
- `orders_df['주문일'].dt.month`: 날짜 열에 `.dt`를 붙이면 연·월·일·요일 같은 부분을 꺼낼 수 있습니다.

```python
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
```

코드 뒷부분에서 `category_sales.columns = [...]`로 열 이름을 다시 붙인 이유가 보이나요? `agg()`에 열마다 집계를 여러 개 요청하면 20.4절에서 본 것처럼 열 이름이 `('주문금액', 'sum')` 같은 두 층 구조가 됩니다. 읽기도 불편하고 열을 꺼내 쓰기도 번거로우니, 순서에 맞춰 '총매출', '평균주문액'처럼 한 층짜리 이름으로 바꾼 거예요. 이름만 바꿨으니 개수와 순서가 집계 순서와 정확히 맞아야 합니다.

`nunique`는 **중복을 뺀 개수**입니다. 한 고객이 여러 번 주문해도 한 명으로 세죠. 그래서 '객단가'(고객 한 명이 쓴 평균 금액)는 총매출을 주문 건수가 아니라 고객 수로 나눕니다.

결과를 보면 다섯 카테고리의 평균 주문액이 모두 25000원 언저리입니다. 모든 카테고리의 금액을 같은 분포에서 뽑았기 때문이에요. 로그정규분포에서 `mean=10, sigma=0.5`로 뽑으면 이론상 평균이 약 24959원(e의 10.125제곱)이 되는데, 실제 결과가 거기에 잘 붙어 있습니다.

## 20.7 시계열 데이터 분석

체중을 매일 재면 하루하루 숫자가 들쭉날쭉합니다. 어제 짠 음식을 먹었는지, 물을 얼마나 마셨는지에 따라 1kg씩 왔다 갔다 하죠. 그래서 다이어트가 잘되고 있는지는 **최근 일주일 평균**으로 보는 게 정확합니다. 하루하루의 출렁임은 지우고 큰 흐름만 남기는 거예요.

이렇게 시간 순서대로 쌓인 데이터를 **시계열(time series)** 이라고 하고, 방금 말한 "최근 N일 평균"을 **이동평균(moving average)** 이라고 합니다. 주식 차트에 겹쳐 그려진 5일선, 20일선, 60일선이 바로 이것이에요.

### 시계열 데이터 처리

예제는 2년 치 가상 주가를 만든 뒤 주말을 빼고, 날짜에서 연도와 월을 꺼내고, 하루 수익률과 이동평균을 계산합니다.

- `stock_data['날짜'].dt.weekday < 5`: 요일 번호는 월요일이 0, 일요일이 6입니다. 5 미만이면 평일이죠. 이 조건으로 행을 걸러 주말을 뺍니다.
- `reset_index(drop=True)`: 행을 걸러 내면 인덱스에 구멍이 생깁니다(5, 6이 빠진 0, 1, 2, 3, 4, 7, …). 0부터 다시 번호를 매기고, 옛 번호는 버립니다.
- `pct_change()`: 바로 앞 행과 비교한 **변화율**입니다. 첫 행은 비교할 앞 행이 없으니 `NaN`이 돼요.
- `rolling(window=5).mean()`: 자기 자신을 포함한 최근 5개 값의 평균입니다. 처음 4행은 값이 5개가 안 모여서 `NaN`이 됩니다. 60일 이동평균이면 처음 59행이 `NaN`이고요.

```python
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
```

출력된 데이터 샘플의 첫 날짜가 2023년 1월 1일이 아니라 1월 2일인 것을 보세요. 2023년 1월 1일이 일요일이라 걸러졌기 때문입니다. 주말을 빼고 나면 2년 치 731일 가운데 522일이 남아요.

가격은 70000원에서 출발해 매일 조금씩 움직이는 값(`cumsum`으로 쌓은 랜덤워크), 2년 동안 0원에서 5000원까지 고르게 오르는 추세(`trend`), 하루하루의 큰 출렁임(표준편차 500원)을 더해 만들었습니다. 그래서 첫 주의 종가는 69000~70000원대인데, 마지막 주에는 74000~75000원대로 올라 있어요.

마지막 다섯 줄을 보면 종가는 74060원에서 75323원 사이를 오르내리는데, 5일 이동평균은 그보다 좁게, 60일 이동평균은 74772원에서 74839원 사이로 거의 움직이지 않습니다. 평균을 내는 기간이 길수록 하루하루의 출렁임이 더 많이 지워지는 거예요. 대신 긴 이동평균은 실제 흐름이 바뀌어도 늦게 따라옵니다. 그래서 짧은 선과 긴 선을 함께 보면서 "최근 흐름이 장기 흐름보다 위에 있나 아래에 있나"를 비교하는 것이죠.

## 20.8 종합 프로젝트: 온라인 쇼핑몰 데이터 분석

이제 지금까지 배운 것을 한 번에 써 볼 차례입니다. 쇼핑몰 사장님이 이렇게 묻는다고 해 봅시다. "우리 가게, 무엇이 잘 팔리고 누가 단골이야?"

### 데이터 준비와 전처리

실제 쇼핑몰 데이터는 보통 한 표에 모여 있지 않습니다. 고객 정보는 고객 표에, 상품 정보는 상품 표에, 주문 기록은 주문 표에 따로 있죠. 같은 고객 주소를 주문할 때마다 적으면 낭비이고, 주소가 바뀌면 모든 주문을 고쳐야 하니까요. 18장에서 본 정규화와 같은 생각입니다.

그래서 분석하기 전에 표를 **합칩니다**. `merge()`는 SQL의 JOIN과 같은 일을 해요. `orders.merge(customers, on='고객ID')`는 두 표에서 고객ID가 같은 행끼리 옆으로 붙입니다. 주문 표에는 고객ID만 있었는데, 합치고 나면 그 고객의 연령·성별·지역이 주문 옆에 따라붙죠. 여기에 상품 표까지 한 번 더 합치면 주문 한 건에 필요한 정보가 한 줄에 모입니다.

데이터를 만드는 코드의 `p=[0.25, 0.2, ...]`는 각 지역이 뽑힐 **확률**입니다. 서울 25%, 경기 20%처럼 실제와 비슷하게 치우치게 한 거예요. 확률을 모두 더하면 1이 되어야 합니다. 마지막의 `clip(18, 70)`은 18보다 작은 나이는 18로, 70보다 큰 나이는 70으로 잘라 냅니다.

```python
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
```

`shape`는 (행 수, 열 수)입니다. 결과 `(5000, 14)`는 주문 5000건이 그대로 남아 있고, 주문 표의 5개 열에 고객 표와 상품 표의 열이 4개씩 붙고, 마지막에 계산한 주문금액 열까지 더해 14개가 됐다는 뜻이에요. 합친 뒤 행 수가 줄지 않았다는 것은 모든 주문의 고객ID와 상품ID가 짝을 찾았다는 확인이기도 합니다. `merge()`는 기본적으로 양쪽에 모두 있는 행만 남기거든요. 출력 가운데의 `...`는 열이 너무 많아서 pandas가 가운데 열을 생략해 보여 준 표시입니다.

### 비즈니스 인사이트 분석

사장님의 질문을 세 개로 나눠서 답합니다.

1. **장사는 얼마나 됐나?** 총매출, 주문 건수, 평균 주문가, 고객 수.
2. **무엇이 잘 팔리나?** 카테고리별 매출과 시장점유율.
3. **누가 단골인가?** 고객을 등급으로 나누는 **RFM 분석**.

RFM은 마케팅에서 오래 써 온 고객 분류법으로, 세 글자가 세 가지 질문입니다.

- **R(Recency, 최근성)**: 마지막으로 산 게 언제인가? 최근일수록 좋습니다.
- **F(Frequency, 빈도)**: 얼마나 자주 샀나? 많을수록 좋습니다.
- **M(Monetary, 금액)**: 모두 얼마나 썼나? 많을수록 좋습니다.

동네 단골 식당 사장님이 머릿속으로 하는 계산과 같아요. "요즘도 자주 오고, 올 때마다 많이 시키는 손님"이 최고의 단골이죠. 코드에서는 각 값을 `pd.qcut()`으로 **고객 수가 같은 다섯 구간**으로 나눠 1~5점을 줍니다. 최근성은 **며칠 전에 샀는지**라서 숫자가 작을수록 좋으니, 라벨을 `[5,4,3,2,1]`로 거꾸로 붙인 점을 눈여겨보세요.

```python
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
```

결과를 사장님께 보고하듯 읽어 봅시다.

1번에서 고객 500명이 주문 5000건을 했으니 한 명당 평균 10번 주문했습니다. 2번에서는 스포츠 카테고리가 매출의 23.6%로 1위예요. 상품 50개의 카테고리를 무작위로 정했더니 스포츠 상품이 11개로 가장 많이 뽑혔고(전자제품은 6개), 그만큼 주문도 많이 몰린 결과입니다. 이처럼 "왜 1위인가?"를 따라가 보면 상품 구성 같은 다른 원인이 나오기도 하니, 순위만 보고 결론을 내리지 않는 습관이 중요해요.

3번의 고객 등급은 이렇게 읽습니다. Champions(최근에, 자주, 많이 산 고객) 76명은 평균 구매빈도 13.7회로 가장 충성스럽고, At Risk(한동안 사지 않은 고객) 136명은 평균 최근성이 198.9일로 가장 오래 발길이 끊겼어요. 사장님이라면 At Risk 고객에게 "다시 와 주세요" 쿠폰을 보내고 싶어지겠죠? 이게 분석이 **행동**으로 이어지는 순간입니다.

`customer_segment()` 함수는 위에서부터 차례로 조건을 검사해 처음 맞는 등급을 돌려준다는 점도 기억해 두세요. 세 점수가 모두 4점 이상인 고객은 R만 보고도 New Customers에 해당하지만, 그보다 먼저 검사하는 Champions로 분류됩니다. 등급 규칙을 바꾸고 싶으면 조건의 **순서**부터 생각해야 해요.

> **Q. 구매빈도에만 `rank(method='first')`를 붙인 이유는 뭔가요?**
> 구매빈도는 3회, 10회, 12회처럼 정수라서 같은 값을 가진 고객이 아주 많습니다. 이 상태로 다섯 구간을 나누면 같은 값끼리는 같은 구간에 들어가야 하니 구간 크기가 고르지 않아요. 이 예제 데이터로 직접 나눠 보면 117명, 116명, 106명, 91명, 70명으로 나뉩니다. `rank(method='first')`는 같은 값이라도 먼저 나온 순서대로 1, 2, 3, … 서로 다른 순위를 매겨 주므로, 이 순위로 나누면 정확히 100명씩 다섯 구간이 됩니다. 값이 겹칠 일이 거의 없는 최근성이나 구매금액에는 필요 없었던 거고요.

## 20.9 데이터 내보내기와 보고서 생성

분석은 다른 사람에게 전해졌을 때 비로소 쓸모가 생깁니다. 사장님이 파이썬을 열어 볼 리는 없으니, 결과를 **사장님이 열 수 있는 파일**로 저장해야죠. 이 절의 예제는 같은 결과를 세 가지 형식으로 저장합니다.

| 형식 | 누가 쓰나 | 특징 |
|---|---|---|
| CSV | 거의 모든 프로그램 | 쉼표로 구분한 텍스트. 가볍지만 시트가 하나뿐 |
| Excel | 사람(사장님, 기획팀) | 시트 여러 장을 한 파일에. `openpyxl` 필요 |
| JSON | 다른 프로그램, 웹 | 딕셔너리 그대로. 17장에서 다룬 `json` 모듈 사용 |

### 다양한 형식으로 데이터 내보내기

CSV를 저장할 때 `encoding='utf-8-sig'`를 쓴 이유가 궁금할 거예요. 그냥 `utf-8`로 저장한 한글 CSV를 윈도우용 엑셀에서 더블클릭해 열면 한글이 깨지는 경우가 많습니다. `utf-8-sig`는 파일 맨 앞에 "이 파일은 UTF-8입니다"라는 작은 표식(BOM)을 붙여서, 엑셀이 인코딩을 알아보게 해 줍니다. 엑셀 저장에 쓴 `pd.ExcelWriter`는 `with` 문과 함께 쓰면 블록이 끝날 때 파일을 알아서 닫아 주고, 그 안에서 `to_excel()`을 여러 번 부르면 시트가 한 장씩 늘어나요.

```python
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
```

JSON 부분에서는 `int(total_revenue)`처럼 굳이 `int()`로 감싼 곳이 있습니다. pandas의 `sum()`이 돌려주는 값은 파이썬의 `int`가 아니라 NumPy의 `int64`인데, `json` 모듈은 이 자료형을 모릅니다. 감싸지 않으면 `Object of type int64 is not JSON serializable`라는 `TypeError`가 나요. 데이터프레임을 JSON으로 보낼 때 자주 만나는 오류이니 기억해 두세요.

'주요_카테고리'에 쓴 `to_dict('index')`도 눈여겨보세요. `category_performance`의 카테고리 이름은 열이 아니라 **인덱스**에 들어 있습니다. `'index'`를 쓰면 인덱스가 바깥 키가 되어 `{"스포츠": {"총매출": 19713266, ...}, "식품": {...}}`처럼 이름이 살아남아요. 비슷한 `to_dict('records')`는 행마다 `{"총매출": ..., "주문건수": ...}` 딕셔너리를 만든 리스트를 돌려주는데, 인덱스를 버리기 때문에 숫자만 남고 **어느 카테고리인지 이름이 사라집니다**. 저장한 파일은 꼭 한 번 열어서 이런 것을 확인하세요. 이것도 분석의 일부입니다.

## 20.10 연습문제

다음 문제들을 해결하여 데이터 분석 실력을 향상시켜보세요. 어느 문제든 순서는 같습니다. 질문을 숫자로 바꾸고(무엇을 계산하면 답이 되나?), 필요한 열을 `groupby()`나 `merge()`로 모으고, 결과를 표와 그래프로 확인하세요. 문제마다 실마리를 하나씩 적어 둡니다.

### 문제 1: 매출 트렌드 분석
월별 매출 트렌드를 분석하고, 전월 대비 성장률을 계산하세요.

실마리: `orders_merged['주문일시'].dt.month`로 월을 꺼내 `groupby()`로 월별 합계를 내고, 20.7절의 `pct_change()`를 쓰면 전월 대비 변화율이 나옵니다.

### 문제 2: 고객 생애 가치 계산
각 고객의 평균 주문 간격, 예상 잔존 기간, 생애 가치를 계산하세요.

실마리: 고객별로 주문일시를 정렬한 다음 `diff()`로 바로 앞 주문과의 차이를 구하면 주문 간격이 됩니다.

### 문제 3: 상품 추천 시스템
고객의 구매 패턴을 바탕으로 간단한 상품 추천 로직을 구현하세요.

실마리: "이 고객이 가장 많이 산 카테고리에서, 아직 안 산 인기 상품"처럼 규칙 하나로 시작하세요.

### 문제 4: 계절성 분석
계절별 판매 패턴을 분석하고 시각화하세요.

실마리: 월을 봄·여름·가을·겨울로 바꾸는 딕셔너리를 만들어 `map()`으로 새 열을 만든 뒤 묶어 보세요. 20.8절의 주문 데이터는 1시간 간격으로 5000건이라 2023년 7월 28일에서 끝납니다. 사계절을 모두 보려면 데이터부터 다시 만들어야 해요.

### 문제 5: A/B 테스트 분석
두 개의 다른 마케팅 캠페인 효과를 통계적으로 비교 분석하세요.

실마리: 두 그룹의 평균 차이가 우연인지 아닌지를 따지는 것이 핵심입니다. 평균만 비교하지 말고 표준편차와 표본 수도 함께 보세요.

## 20.11 다음 장 미리보기

이 장에서는 데이터를 정리하고, 묶고, 요약하고, 그림으로 보는 방법을 배웠습니다. 모두 **이미 일어난 일을 설명하는** 작업이었죠. "지난달 무엇이 잘 팔렸나?", "어떤 고객이 단골인가?"처럼요.

다음 질문은 자연스럽게 미래로 향합니다. "다음 달에는 얼마나 팔릴까?", "이 고객은 곧 떠날까?" 데이터에서 규칙을 스스로 배워 이런 질문에 답하는 프로그램을 만드는 것이 **머신러닝**입니다. 머신러닝과 딥러닝은 이 책의 2권(딥러닝 편)에서 이어서 다룹니다. 2권에서도 데이터는 이 장에서 익힌 pandas 데이터프레임과 NumPy 배열의 모습으로 들어오니, 이 장의 도구에 충분히 익숙해진 다음 넘어가세요.

---

## 주요 학습 내용 요약

1. **NumPy**: 수치 연산과 배열 처리의 기초
2. **Pandas**: 구조화된 데이터 조작과 분석
3. **데이터 클리닝**: 결측치와 이상값 처리 방법
4. **탐색적 데이터 분석**: 기술 통계와 그룹별 요약, 이상값 확인
5. **시각화**: Matplotlib과 Seaborn을 활용한 그래프 작성
6. **데이터 집계**: GroupBy를 활용한 복잡한 분석
7. **시계열 분석**: 시간에 따른 데이터 패턴 분석
8. **종합 프로젝트**: 실제 비즈니스 문제 해결
9. **데이터 내보내기**: 분석 결과 저장과 공유

데이터 분석의 전체 흐름, 즉 정리하고, 묶고, 요약하고, 그림으로 보는 과정을 한 바퀴 돌아봤습니다. 이 데이터로 예측 모델을 만드는 방법은 2권(딥러닝 편)에서 이어집니다.