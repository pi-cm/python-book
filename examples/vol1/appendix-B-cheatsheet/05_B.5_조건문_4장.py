"""1권 부록 B. 한눈에 보는 파이썬 — B.5 조건문 (4장)

원고: manuscript/appendix/B-cheatsheet.md (196줄부터)
"""

# ---- 원고 196줄 ----
score = 85
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
else:
    grade = "C"
print(grade)                               # B
print("합격" if score >= 60 else "불합격")  # 합격
print(80 <= score < 90)                    # True

# ---- 원고 211줄 ----
def describe(cmd):
    match cmd:
        case "quit" | "exit":
            return "종료"
        case ["go", direction]:
            return f"{direction}로 이동"
        case {"action": "say", "text": str(text)}:
            return f"말하기: {text}"
        case int(n) if n < 0:
            return "음수"
        case _:
            return "알 수 없음"

print(describe("exit"))                            # 종료
print(describe(["go", "북쪽"]))                    # 북쪽로 이동
print(describe({"action": "say", "text": "안녕"}))  # 말하기: 안녕
print(describe(-3), describe(3.5))                 # 음수 알 수 없음
