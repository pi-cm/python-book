"""1권 Chapter 3. 연산과 표현식 — 3.6 연산자 우선순위와 결합성

원고: manuscript/chapters/03-operators.md (902줄부터)
"""

# ---- 원고 902줄 ----
# 연산자 우선순위 (높음 → 낮음)
print("=== 연산자 우선순위 테스트 ===")

# 1. 괄호가 최우선
result1 = 2 + 3 * 4      # 14 (곱셈 우선)
result2 = (2 + 3) * 4    # 20 (괄호 우선)
print(f"2 + 3 * 4 = {result1}")
print(f"(2 + 3) * 4 = {result2}")

# 2. 거듭제곱 (**) 
result3 = 2 * 3 ** 2     # 18 (3**2 먼저)
result4 = (2 * 3) ** 2   # 36 (괄호 먼저)
print(f"2 * 3 ** 2 = {result3}")
print(f"(2 * 3) ** 2 = {result4}")

# 3. 단항 연산자 (+, -, ~)
result5 = -3 ** 2        # -9 (-(3**2))
result6 = (-3) ** 2      # 9 ((-3)**2)
print(f"-3 ** 2 = {result5}")
print(f"(-3) ** 2 = {result6}")

# 4. 곱셈, 나눗셈 (*, /, //, %)
result7 = 10 + 2 * 3     # 16
result8 = 10 / 2 - 3     # 2.0
print(f"10 + 2 * 3 = {result7}")
print(f"10 / 2 - 3 = {result8}")

# 5. 덧셈, 뺄셈 (+, -)
result9 = 10 - 3 + 2     # 9 (좌→우 결합)
print(f"10 - 3 + 2 = {result9}")

# 6. 시프트 연산자 (<<, >>)
result10 = 8 + 2 << 1    # (8 + 2) << 1 = 20
result11 = 8 + (2 << 1)  # 8 + 4 = 12
print(f"8 + 2 << 1 = {result10}")
print(f"8 + (2 << 1) = {result11}")

# 7. 비트 AND (&)
result12 = 5 | 3 & 2     # 5 | (3 & 2) = 5 | 2 = 7
print(f"5 | 3 & 2 = {result12}")

# 8. 비트 XOR (^)
result13 = 5 | 3 ^ 2     # 5 | (3 ^ 2) = 5 | 1 = 5
print(f"5 | 3 ^ 2 = {result13}")

# 9. 비트 OR (|)
# 위 예제 참조

# 10. 비교 연산자 (==, !=, <, >, <=, >=, is, is not, in, not in)
result14 = 5 + 3 > 7     # True
result15 = 1 < 2 < 3     # True (연쇄 비교)
print(f"5 + 3 > 7: {result14}")
print(f"1 < 2 < 3: {result15}")

# 11. 논리 NOT (not)
result16 = not 5 > 3     # False
print(f"not 5 > 3: {result16}")

# 12. 논리 AND (and)
result17 = True and False or True   # True (and가 or보다 우선)
print(f"True and False or True: {result17}")

# 13. 논리 OR (or)
# 위 예제 참조

# 복잡한 표현식 예제
복잡한_표현식 = 2 + 3 * 4 ** 2 > 50 and not False or 1 in [1, 2, 3]
print(f"복잡한 표현식: {복잡한_표현식}")
# 계산 순서: 4**2=16, 3*16=48, 2+48=50, 50>50=False, not False=True, 
# False and True=False, 1 in [1,2,3]=True, False or True=True

# ---- 원고 979줄 ----
print("\n=== 결합성 테스트 ===")

# 좌결합성 (대부분의 연산자)
result1 = 10 - 5 - 2     # ((10 - 5) - 2) = 3
result2 = 20 / 4 / 2     # ((20 / 4) / 2) = 2.5
print(f"10 - 5 - 2 = {result1}")
print(f"20 / 4 / 2 = {result2}")

# 우결합성 (거듭제곱, 할당)
result3 = 2 ** 3 ** 2    # (2 ** (3 ** 2)) = 2 ** 9 = 512
result4 = 2 ** (3 ** 2)  # 명시적 표현
print(f"2 ** 3 ** 2 = {result3}")
print(f"2 ** (3 ** 2) = {result4}")

# 할당 연산자의 우결합성
a = b = c = 5  # c = 5, b = c, a = b
print(f"a = b = c = 5: a={a}, b={b}, c={c}")

# 삼항 연산자 (조건식)
x = 10
result5 = "양수" if x > 0 else "음수" if x < 0 else "영"
print(f"삼항 연산자 결과: {result5}")

# ---- 원고 1006줄 ----
import math
import re

class 고급계산기:
    """한국어를 지원하는 고급 과학 계산기"""
    
    # 상수 정의
    상수들 = {
        "파이": math.pi,
        "π": math.pi,
        "이": math.e,
        "e": math.e,
        "무한대": math.inf,
        "∞": math.inf
    }
    
    # 함수 매핑
    함수들 = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "sinh": math.sinh,
        "cosh": math.cosh,
        "tanh": math.tanh,
        "log": math.log10,
        "ln": math.log,
        "sqrt": math.sqrt,
        "제곱근": math.sqrt,
        "abs": abs,
        "절댓값": abs,
        "ceil": math.ceil,
        "올림": math.ceil,
        "floor": math.floor,
        "내림": math.floor,
        "round": round,
        "반올림": round
    }
    
    def __init__(self):
        self.히스토리 = []
        self.변수들 = {}
    
    def 전처리(self, 표현식: str) -> str:
        """표현식 전처리"""
        # 한국어 상수 치환
        for 한국어, 값 in self.상수들.items():
            표현식 = 표현식.replace(한국어, str(값))
        
        # 한국어 연산자 치환
        표현식 = 표현식.replace("의", "*")
        표현식 = 표현식.replace("곱하기", "*")
        표현식 = 표현식.replace("나누기", "/")
        표현식 = 표현식.replace("더하기", "+")
        표현식 = 표현식.replace("빼기", "-")
        표현식 = 표현식.replace("제곱", "**")
        
        # 괄호 처리
        표현식 = 표현식.replace("（", "(").replace("）", ")")
        
        # 공백 제거
        표현식 = re.sub(r'\s+', '', 표현식)
        
        return 표현식
    
    def 후처리_함수(self, 표현식: str) -> str:
        """함수 호출 처리"""
        # 함수 패턴 매칭
        함수_패턴 = r'([a-zA-Z가-힣]+)\(([^)]+)\)'
        
        def 함수_치환(match):
            함수명 = match.group(1)
            인자 = match.group(2)
            
            if 함수명 in self.함수들:
                try:
                    인자값 = eval(인자, {"__builtins__": {}}, self.변수들)
                    결과 = self.함수들[함수명](인자값)
                    return str(결과)
                except:
                    raise ValueError(f"함수 {함수명}의 인자가 올바르지 않습니다: {인자}")
            else:
                raise ValueError(f"알 수 없는 함수: {함수명}")
        
        # 함수 치환 반복 (중첩 함수 처리)
        이전_표현식 = ""
        while 이전_표현식 != 표현식:
            이전_표현식 = 표현식
            표현식 = re.sub(함수_패턴, 함수_치환, 표현식)
        
        return 표현식
    
    def 계산(self, 표현식: str):
        """메인 계산 함수"""
        원본_표현식 = 표현식
        
        try:
            # 전처리
            표현식 = self.전처리(표현식)
            
            # 함수 처리
            표현식 = self.후처리_함수(표현식)
            
            # 변수 할당 확인
            if "=" in 표현식 and not any(op in 표현식 for op in ["==", "!=", "<=", ">="]):
                변수명, 값_표현식 = 표현식.split("=", 1)
                변수명 = 변수명.strip()
                값 = eval(값_표현식, {"__builtins__": {}}, self.변수들)
                self.변수들[변수명] = 값
                결과 = f"{변수명} = {값}"
            else:
                # 일반 계산
                결과 = eval(표현식, {"__builtins__": {}}, self.변수들)
            
            # 히스토리 저장
            self.히스토리.append(f"{원본_표현식} = {결과}")
            
            return 결과
            
        except ZeroDivisionError:
            return "오류: 0으로 나눌 수 없습니다"
        except ValueError as e:
            return f"오류: {e}"
        except Exception as e:
            return f"계산 오류: {e}"
    
    def 히스토리_출력(self):
        """계산 히스토리 출력"""
        if not self.히스토리:
            print("계산 히스토리가 없습니다.")
            return
        
        print("=== 계산 히스토리 ===")
        for i, 항목 in enumerate(self.히스토리[-10:], 1):  # 최근 10개만
            print(f"{i:2d}. {항목}")
    
    def 변수_출력(self):
        """저장된 변수들 출력"""
        if not self.변수들:
            print("저장된 변수가 없습니다.")
            return
        
        print("=== 저장된 변수들 ===")
        for 이름, 값 in self.변수들.items():
            print(f"{이름} = {값}")

# 계산기 사용 예제
def 계산기_데모():
    calc = 고급계산기()
    
    테스트_식들 = [
        "2 + 3 * 4",
        "sin(파이/2)",
        "제곱근(16)",
        "x = 10",
        "y = x * 2",
        "x + y",
        "절댓값(-5)",
        "2의 3제곱",
        "log(100)",
        "반올림(3.7)"
    ]
    
    print("고급 계산기 데모")
    print("=" * 40)
    
    for 식 in 테스트_식들:
        결과 = calc.계산(식)
        print(f"{식} = {결과}")
    
    print("\n")
    calc.히스토리_출력()
    print("\n")
    calc.변수_출력()

# 데모 실행
계산기_데모()
