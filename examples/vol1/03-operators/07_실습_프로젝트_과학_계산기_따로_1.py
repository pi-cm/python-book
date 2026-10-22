"""1권 Chapter 3. 연산과 표현식 — 실습 프로젝트: 과학 계산기

원고: manuscript/chapters/03-operators.md (1194줄부터)
"""

# ---- 원고 1194줄 ----
def 대화형_계산기():
    """대화형 과학 계산기"""
    calc = 고급계산기()
    
    print("한국어 과학 계산기")
    print("=" * 50)
    print("사용법:")
    print("  - 기본 연산: 2 + 3, 10 * 5, 2**3")
    print("  - 함수: sin(파이/2), 제곱근(16), 절댓값(-5)")
    print("  - 변수: x = 10, y = x * 2")
    print("  - 상수: 파이, 이, 무한대")
    print("  - 명령: 히스토리, 변수, 도움말, 종료")
    print("=" * 50)
    
    while True:
        try:
            입력 = input("\n계산식> ").strip()
            
            if not 입력:
                continue
            
            # 명령어 처리
            match 입력:
                case "종료" | "exit" | "quit":
                    print("계산기를 종료합니다.")
                    break
                
                case "히스토리" | "history":
                    calc.히스토리_출력()
                
                case "변수" | "vars":
                    calc.변수_출력()
                
                case "도움말" | "help":
                    print("""
사용 가능한 함수들:
  삼각함수: sin, cos, tan, asin, acos, atan
  쌍곡함수: sinh, cosh, tanh
  로그함수: log (상용로그), ln (자연로그)
  기타: 제곱근/sqrt, 절댓값/abs, 올림/ceil, 내림/floor, 반올림/round

상수:
  파이/π = {math.pi:.6f}
  이/e = {math.e:.6f}
  무한대/∞ = ∞

연산자:
  +, -, *, /, //, %, ** (제곱)
  비교: ==, !=, <, >, <=, >=
  논리: and, or, not
  비트: &, |, ^, ~, <<, >>
                    """)
                
                case "클리어" | "clear":
                    calc.히스토리.clear()
                    calc.변수들.clear()
                    print("히스토리와 변수가 모두 지워졌습니다.")
                
                case _:
                    # 계산 수행
                    결과 = calc.계산(입력)
                    print(f"결과: {결과}")
        
        except KeyboardInterrupt:
            print("\n\n계산기를 종료합니다.")
            break
        except EOFError:
            print("\n계산기를 종료합니다.")
            break

# 대화형 계산기 실행 (실제 사용 시 주석 해제)
# 대화형_계산기()
