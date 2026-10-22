"""1권 Chapter 6: 리스트와 튜플 — 6.2 리스트 메서드

원고: manuscript/chapters/06-lists-tuples.md (96줄부터)
"""

# ---- 원고 96줄 ----
korean_names = ["김철수", "이영희"]

# append(): 끝에 하나 추가
korean_names.append("박민수")
print(f"append 후: {korean_names}")

# insert(): 지정 위치에 추가
korean_names.insert(1, "최지영")
print(f"insert 후: {korean_names}")

# extend(): 여러 요소 추가
korean_names.extend(["정수진", "한미영"])
print(f"extend 후: {korean_names}")

# + 연산자로 추가
new_names = korean_names + ["윤태호", "강예린"]
print(f"+ 연산 후: {new_names}")

# ---- 원고 130줄 ----
subjects = ["국어", "영어", "수학", "과학", "역사", "미술", "음악"]

# remove(): 값으로 제거 (첫 번째 일치 항목)
subjects.remove("미술")
print(f"remove 후: {subjects}")

# pop(): 인덱스로 제거 후 반환
removed = subjects.pop(2)  # 수학 제거
print(f"제거된 과목: {removed}")
print(f"pop 후: {subjects}")

# pop(): 마지막 요소 제거
last = subjects.pop()
print(f"마지막 과목: {last}")
print(f"마지막 pop 후: {subjects}")

# clear(): 모든 요소 제거
test_list = subjects.copy()
test_list.clear()
print(f"clear 후: {test_list}")

# del 문: 슬라이스로 제거
del subjects[1:3]
print(f"del 후: {subjects}")

# ---- 원고 164줄 ----
점수들 = [90, 45, 30, 80, 55]
for 점수 in 점수들:
    if 점수 < 60:
        점수들.remove(점수)
print(점수들)  # [90, 30, 80] - 30이 살아남았다!

점수들 = [90, 45, 30, 80, 55]
print([점수 for 점수 in 점수들 if 점수 >= 60])  # [90, 80]

# ---- 원고 190줄 ----
scores = [85, 92, 78, 95, 88, 92, 76, 89]

# index(): 값의 위치 찾기
position = scores.index(95)
print(f"95점의 위치: {position}")

# count(): 값의 개수 세기
count_92 = scores.count(92)
print(f"92점의 개수: {count_92}")

# sort(): 원본 정렬 (오름차순)
scores.sort()
print(f"오름차순 정렬: {scores}")

# sort(): 내림차순 정렬
scores.sort(reverse=True)
print(f"내림차순 정렬: {scores}")

# sorted(): 새로운 리스트 반환
original_scores = [85, 92, 78, 95, 88]
sorted_scores = sorted(original_scores)
print(f"원본: {original_scores}")
print(f"정렬된 복사본: {sorted_scores}")

# reverse(): 순서 뒤집기
korean_alphabet = ["ㄱ", "ㄴ", "ㄷ", "ㄹ", "ㅁ"]
korean_alphabet.reverse()
print(f"뒤집힌 자음: {korean_alphabet}")

# ---- 원고 227줄 ----
korean_words = ["사과", "바나나", "딸기", "포도", "오렌지"]

# 한글 가나다 순 정렬
korean_words.sort()
print(f"가나다순: {korean_words}")

# 길이순 정렬
korean_words.sort(key=len)
print(f"길이순: {korean_words}")

# 복잡한 정렬 (길이 우선, 같으면 가나다순)
korean_words.sort(key=lambda x: (len(x), x))
print(f"길이+가나다순: {korean_words}")
