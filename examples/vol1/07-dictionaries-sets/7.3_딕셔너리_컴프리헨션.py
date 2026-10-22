"""1권 Chapter 7: 딕셔너리와 집합 — 7.3 딕셔너리 컴프리헨션

원고: manuscript/chapters/07-dictionaries-sets.md (212줄부터)
"""

# ---- 원고 212줄 ----
# 숫자와 제곱의 딕셔너리
squares = {x: x**2 for x in range(1, 11)}
print(f"제곱수 딕셔너리: {squares}")

# 한글 자음과 순서
consonants = ["ㄱ", "ㄴ", "ㄷ", "ㄹ", "ㅁ", "ㅂ", "ㅅ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]
consonant_order = {char: idx + 1 for idx, char in enumerate(consonants)}
print(f"자음 순서: {consonant_order}")

# 문자열에서 문자 빈도 계산
text = "안녕하세요 파이썬 프로그래밍"
char_frequency = {char: text.count(char) for char in set(text) if char != ' '}
print(f"문자 빈도: {char_frequency}")

# 조건부 딕셔너리 컴프리헨션
korean_numbers = ["하나", "둘", "셋", "넷", "다섯", "여섯", "일곱", "여덟", "아홉", "열"]
long_numbers = {num: len(num) for num in korean_numbers if len(num) >= 2}
print(f"2글자 이상 숫자: {long_numbers}")

# ---- 원고 237줄 ----
# 구구단 딕셔너리
multiplication_table = {
    i: {j: i * j for j in range(1, 10)} 
    for i in range(2, 10)
}
print(f"3단: {multiplication_table[3]}")

# 학급별 학생 성적 구조
classes = ["A반", "B반", "C반"]
subjects = ["국어", "영어", "수학"]
class_structure = {
    cls: {subject: [] for subject in subjects}
    for cls in classes
}
print(f"A반 구조: {class_structure['A반']}")

# 지역별 날씨 데이터 구조
regions = ["서울", "부산", "대구"]
weather_data = {
    region: {
        "온도": None,
        "습도": None, 
        "날씨": None
    } for region in regions
}
print(f"부산 날씨 구조: {weather_data['부산']}")
