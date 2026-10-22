"""1권 Chapter 6: 리스트와 튜플 — 6.6 시퀀스 공통 연산

원고: manuscript/chapters/06-lists-tuples.md (485줄부터)
"""

# ---- 원고 485줄 ----
korean_foods = ["김치", "불고기", "비빔밥", "잡채", "떡볶이"]

# in 연산자
print(f"김치가 있나요? {'김치' in korean_foods}")
print(f"스파게티가 있나요? {'스파게티' in korean_foods}")

# not in 연산자
if "피자" not in korean_foods:
    print("피자는 한국 음식이 아닙니다")

# 부분 문자열 검사
food_with_rice = [food for food in korean_foods if "밥" in food]
print(f"밥이 들어간 음식: {food_with_rice}")

# ---- 원고 505줄 ----
# 리스트 연결
seoul_districts = ["강남구", "서초구", "송파구"]
busan_districts = ["해운대구", "부산진구", "동래구"]
all_districts = seoul_districts + busan_districts
print(f"모든 구: {all_districts}")

# 튜플 연결
korean_vowels = ("ㅏ", "ㅓ", "ㅗ", "ㅜ")
additional_vowels = ("ㅡ", "ㅣ")
all_vowels = korean_vowels + additional_vowels
print(f"모든 모음: {all_vowels}")

# 반복
emphasis = ["좋아"] * 3
print(f"강조: {emphasis}")

separator = ("=",) * 10
print(f"구분선: {separator}")

# ---- 원고 530줄 ----
temperatures = [15, 28, 32, 19, 25, 30, 17]

print(f"측정 횟수: {len(temperatures)}")
print(f"최고 기온: {max(temperatures)}도")
print(f"최저 기온: {min(temperatures)}도")
print(f"총합: {sum(temperatures)}도")
print(f"평균: {sum(temperatures) / len(temperatures):.1f}도")

# 한글에서 최대/최소
korean_words = ["가위", "바위", "보", "사과", "하늘"]
print(f"사전순 첫 번째: {min(korean_words)}")
print(f"사전순 마지막: {max(korean_words)}")
print(f"가장 긴 단어: {max(korean_words, key=len)}")
