"""1권 Chapter 4. 조건문과 분기 — 4.5 예외 처리와 조건문의 조화

원고: manuscript/chapters/04-control-flow.md (847줄부터)
"""

# ---- 원고 847줄 ----
# EAFP vs LBYL 방식

# LBYL (Look Before You Leap) - 실행 전에 확인
def LBYL_방식_파일읽기(파일명):
    import os
    if os.path.exists(파일명):
        if os.path.isfile(파일명):
            if os.access(파일명, os.R_OK):
                try:
                    with open(파일명, 'r', encoding='utf-8') as f:
                        return f.read()
                except Exception as e:
                    return f"파일 읽기 오류: {e}"
            else:
                return "파일 읽기 권한이 없습니다"
        else:
            return "디렉토리입니다, 파일이 아닙니다"
    else:
        return "파일이 존재하지 않습니다"

# EAFP (Easier to Ask for Forgiveness than Permission) - 일단 시도 후 처리
def EAFP_방식_파일읽기(파일명):
    try:
        with open(파일명, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "파일이 존재하지 않습니다"
    except PermissionError:
        return "파일 읽기 권한이 없습니다"
    except IsADirectoryError:
        return "디렉토리입니다, 파일이 아닙니다"
    except Exception as e:
        return f"파일 읽기 오류: {e}"

# 조건문과 예외처리의 적절한 조합
def 안전한_나눗셈_계산기():
    while True:
        try:
            수식 = input("나눗셈을 입력하세요 (예: 10/2, 종료하려면 'quit'): ")
            
            # 종료 조건
            if 수식.lower() == 'quit':
                break
            
            # 입력 검증
            if '/' not in 수식:
                print("나눗셈 기호(/)가 없습니다.")
                continue
            
            parts = 수식.split('/')
            if len(parts) != 2:
                print("올바른 형식으로 입력해주세요 (숫자/숫자)")
                continue
            
            # 숫자 변환 시도
            try:
                분자 = float(parts[0].strip())
                분모 = float(parts[1].strip())
            except ValueError:
                print("숫자를 올바르게 입력해주세요.")
                continue
            
            # 0으로 나누기 검사
            if 분모 == 0:
                print("0으로 나눌 수 없습니다.")
                continue
            
            결과 = 분자 / 분모
            print(f"{분자} ÷ {분모} = {결과}")
            
        except KeyboardInterrupt:
            print("\n프로그램을 종료합니다.")
            break
        except Exception as e:
            print(f"예상치 못한 오류: {e}")

# 실행 예제 (주석 처리)
# 안전한_나눗셈_계산기()
