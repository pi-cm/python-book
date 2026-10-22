"""1권 Chapter 10: 함수형 프로그래밍 — 10.3 내장 함수: map, filter, reduce

원고: manuscript/chapters/10-functional-programming.md (398줄부터)
"""

# ---- 원고 398줄 ----
# 한국 전통 측정 단위 변환
def convert_traditional_units():
    """한국 전통 단위 변환"""
    
    # 길이 단위 변환 (척, 자, 치, 분)
    modern_lengths_cm = [30, 150, 180, 200, 25]  # cm
    
    # 1척 = 30.3cm
    to_cheok = lambda cm: round(cm / 30.3, 2)
    cheok_lengths = list(map(to_cheok, modern_lengths_cm))
    
    print("길이 단위 변환 (cm → 척):")
    for cm, cheok in zip(modern_lengths_cm, cheok_lengths):
        print(f"{cm}cm = {cheok}척")
    
    # 무게 단위 변환 (관, 근, 량)
    modern_weights_g = [600, 1500, 3750, 37500]  # g
    
    # 1관 = 3.75kg = 3750g, 1근 = 600g, 1량 = 37.5g
    def to_traditional_weight(grams):
        gwan = grams // 3750
        remaining = grams % 3750
        geun = remaining // 600
        remaining = remaining % 600
        ryang = remaining // 37.5
        
        parts = []
        if gwan > 0: parts.append(f"{int(gwan)}관")
        if geun > 0: parts.append(f"{int(geun)}근")
        if ryang > 0: parts.append(f"{ryang:.1f}량")
        
        return " ".join(parts) if parts else "0량"
    
    traditional_weights = list(map(to_traditional_weight, modern_weights_g))
    
    print(f"\n무게 단위 변환 (g → 관/근/량):")
    for g, trad in zip(modern_weights_g, traditional_weights):
        print(f"{g}g = {trad}")

# 한국어 텍스트 전처리
korean_texts = [
    "안녕하세요! 파이썬을 배워봅시다.",
    "데이터 분석이 정말 재미있어요~~~",
    "프로그래밍은 창의적인 활동입니다!!",
    "열심히 공부해서 개발자가 되고 싶습니다 ㅎㅎㅎ"
]

def preprocess_korean_text(text: str) -> dict:
    """한국어 텍스트 전처리"""
    import re
    
    # 특수문자 제거
    cleaned = re.sub(r'[^\w\s가-힣]', '', text)
    
    # 연속된 공백 정리
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # 단어 분리
    words = cleaned.split()
    
    # 글자 수 계산
    char_count = len(text.replace(' ', ''))
    korean_char_count = len(re.findall(r'[가-힣]', text))
    
    return {
        "원문": text,
        "정제문": cleaned,
        "단어수": len(words),
        "총글자수": char_count,
        "한글글자수": korean_char_count,
        "한글비율": f"{korean_char_count/char_count*100:.1f}%" if char_count > 0 else "0%"
    }

print("\n한국어 텍스트 전처리:")
processed_texts = list(map(preprocess_korean_text, korean_texts))

for i, result in enumerate(processed_texts, 1):
    print(f"\n텍스트 {i}:")
    for key, value in result.items():
        print(f"  {key}: {value}")

convert_traditional_units()

# ---- 원고 493줄 ----
# 한국 대학교 정보 필터링
universities = [
    {"이름": "서울대학교", "설립년": 1946, "소재지": "서울", "학생수": 28000, "유형": "국립"},
    {"이름": "연세대학교", "설립년": 1885, "소재지": "서울", "학생수": 38000, "유형": "사립"},
    {"이름": "고려대학교", "설립년": 1905, "소재지": "서울", "학생수": 36000, "유형": "사립"},
    {"이름": "KAIST", "설립년": 1971, "소재지": "대전", "학생수": 10000, "유형": "국립"},
    {"이름": "포항공대", "설립년": 1986, "소재지": "포항", "학생수": 3000, "유형": "사립"},
    {"이름": "부산대학교", "설립년": 1946, "소재지": "부산", "학생수": 30000, "유형": "국립"},
    {"이름": "경희대학교", "설립년": 1949, "소재지": "서울", "학생수": 35000, "유형": "사립"}
]

def demonstrate_university_filtering():
    """대학교 정보 필터링 시연"""
    
    # 서울 소재 대학교
    seoul_universities = list(filter(lambda x: x["소재지"] == "서울", universities))
    print(f"서울 소재 대학교 ({len(seoul_universities)}곳):")
    for uni in seoul_universities:
        print(f"  {uni['이름']} ({uni['설립년']})")
    
    # 100년 이상 된 대학교 (올해 기준)
    from datetime import datetime
    current_year = datetime.now().year
    old_universities = list(filter(
        lambda x: current_year - x["설립년"] >= 100, 
        universities
    ))
    print(f"\n100년 이상 된 대학교 ({len(old_universities)}곳):")
    for uni in old_universities:
        age = current_year - uni["설립년"]
        print(f"  {uni['이름']}: {age}년")
    
    # 학생 수 3만명 이상인 대학교
    large_universities = list(filter(
        lambda x: x["학생수"] >= 30000,
        universities
    ))
    print(f"\n대형 대학교 (3만명 이상, {len(large_universities)}곳):")
    for uni in sorted(large_universities, key=lambda x: x["학생수"], reverse=True):
        print(f"  {uni['이름']}: {uni['학생수']:,}명")
    
    # 복합 조건: 서울 소재 + 사립 + 3만명 이상
    premium_universities = list(filter(
        lambda x: (x["소재지"] == "서울" and 
                  x["유형"] == "사립" and 
                  x["학생수"] >= 30000),
        universities
    ))
    print(f"\n서울 소재 대형 사립대 ({len(premium_universities)}곳):")
    for uni in premium_universities:
        print(f"  {uni['이름']}")

# 한국어 단어 필터링
korean_words = [
    "사과", "apple", "바나나", "banana", "컴퓨터", "computer",
    "프로그래밍", "programming", "안녕하세요", "hello",
    "데이터분석", "data analysis", "머신러닝", "machine learning"
]

def is_korean_word(word: str) -> bool:
    """한국어 단어 판별"""
    import re
    return bool(re.search(r'[가-힣]', word)) and not re.search(r'[a-zA-Z]', word)

def is_mixed_word(word: str) -> bool:
    """한영 혼합 단어 판별"""
    import re
    return bool(re.search(r'[가-힣]', word)) and bool(re.search(r'[a-zA-Z]', word))

print("\n단어 분류:")
korean_only = list(filter(is_korean_word, korean_words))
english_only = list(filter(lambda w: not is_korean_word(w) and not is_mixed_word(w), korean_words))
mixed_words = list(filter(is_mixed_word, korean_words))

print(f"순한글 단어: {korean_only}")
print(f"영어 단어: {english_only}") 
print(f"한영혼합: {mixed_words}")

demonstrate_university_filtering()

# ---- 원고 583줄 ----
from functools import reduce
import operator

def korean_math_operations():
    """한국어 수학 연산 예제"""
    
    number_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    # 곱셈으로 팩토리얼 계산
    factorial_10 = reduce(operator.mul, number_values)
    print(f"10! (팩토리얼): {factorial_10:,}")
    
    # 덧셈으로 합계 계산  
    total_sum = reduce(operator.add, number_values)
    print(f"1부터 10까지 합: {total_sum}")
    
    # 최대값 찾기
    scores = [85, 92, 78, 96, 88, 91, 87]
    max_score = reduce(max, scores)
    print(f"최고 점수: {max_score}")
    
    # 문자열 연결
    korean_regions = ["서울", "부산", "대구", "인천", "광주", "대전", "울산"]
    all_regions = reduce(lambda x, y: f"{x}, {y}", korean_regions)
    print(f"특별시·광역시: {all_regions}")

def analyze_korean_company_data():
    """한국 기업 데이터 분석"""
    
    companies = [
        {"이름": "삼성전자", "매출": 2796890, "직원수": 267800, "업종": "전자"},
        {"이름": "SK하이닉스", "매출": 366020, "직원수": 33690, "업종": "반도체"},
        {"이름": "LG전자", "매출": 748632, "직원수": 75000, "업종": "전자"},
        {"이름": "현대자동차", "매출": 1055210, "직원수": 120000, "업종": "자동차"},
        {"이름": "기아", "매출": 894750, "직원수": 52000, "업종": "자동차"},
        {"이름": "POSCO", "매출": 713680, "직원수": 29000, "업종": "철강"},
        {"이름": "LG화학", "매출": 442010, "직원수": 45000, "업종": "화학"}
    ]
    
    # 총 매출 계산
    total_revenue = reduce(
        lambda acc, company: acc + company["매출"], 
        companies, 
        0
    )
    print(f"\n선정 기업 총 매출: {total_revenue:,} 억원")
    
    # 총 직원 수 계산
    total_employees = reduce(
        lambda acc, company: acc + company["직원수"],
        companies,
        0
    )
    print(f"선정 기업 총 직원 수: {total_employees:,} 명")
    
    # 업종별 집계
    from collections import defaultdict
    
    def group_by_industry(acc, company):
        industry = company["업종"]
        if industry not in acc:
            acc[industry] = {"매출": 0, "직원수": 0, "기업수": 0}
        
        acc[industry]["매출"] += company["매출"]
        acc[industry]["직원수"] += company["직원수"] 
        acc[industry]["기업수"] += 1
        return acc
    
    industry_stats = reduce(group_by_industry, companies, {})
    
    print(f"\n업종별 현황:")
    for industry, stats in industry_stats.items():
        avg_revenue = stats["매출"] / stats["기업수"]
        avg_employees = stats["직원수"] / stats["기업수"]
        print(f"{industry}업:")
        print(f"  총 매출: {stats['매출']:,} 억원")
        print(f"  총 직원: {stats['직원수']:,} 명")
        print(f"  기업당 평균 매출: {avg_revenue:,.0f} 억원")
        print(f"  기업당 평균 직원: {avg_employees:,.0f} 명")
        print()

korean_math_operations()
analyze_korean_company_data()
