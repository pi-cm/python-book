"""1권 Chapter 12: 파일과 예외 처리 — 12.3 예외 처리 기초

원고: manuscript/chapters/12-files-exceptions.md (622줄부터)
"""

# ---- 원고 622줄 ----
for text in ["5", "0", "abc"]:
    try:
        y = 10 / int(text)
    except ZeroDivisionError:      # 0으로 나눴을 때
        print("0으로 나눌 수 없습니다.")
    except ValueError:             # 숫자가 아닌 글자가 들어왔을 때
        print("숫자를 입력하세요.")
    else:                          # 예외가 없었을 때만
        print("결과:", y)
    finally:                       # 무슨 일이 있어도
        print("--- 끝 ---")

# ---- 원고 643줄 ----
import traceback
from typing import Optional, List
import random

def basic_exception_handling():
    """기본 예외 처리 패턴"""
    
    print("1. 기본 try-except 구문:")
    
    # 숫자 입력받기 (시뮬레이션)
    user_inputs = ["25", "abc", "0", "-5", "100"]
    
    for user_input in user_inputs:
        try:
            age = int(user_input)
            print(f"[O] 입력값 '{user_input}' → 나이: {age}세")
            
            # 나이 유효성 검사
            if age < 0:
                raise ValueError("나이는 0보다 작을 수 없습니다")
            elif age > 150:
                raise ValueError("나이는 150을 초과할 수 없습니다")
            
            # 연령대 분류
            if age < 20:
                category = "청소년"
            elif age < 65:
                category = "성인"
            else:
                category = "노인"
            
            print(f"   연령대: {category}")
            
        except ValueError as e:
            print(f"[X] 입력값 '{user_input}' 오류: {e}")
        except Exception as e:
            print(f"[X] 예상치 못한 오류: {e}")

def multiple_exception_handling():
    """다중 예외 처리"""
    
    print("\n2. 다중 예외 처리:")
    
    # 다양한 오류 상황 시뮬레이션
    test_cases = [
        {"operation": "divide", "a": 10, "b": 2},
        {"operation": "divide", "a": 10, "b": 0},  # ZeroDivisionError
        {"operation": "access_list", "lst": [1, 2, 3], "index": 1},
        {"operation": "access_list", "lst": [1, 2, 3], "index": 5},  # IndexError
        {"operation": "access_dict", "d": {"name": "김철수"}, "key": "name"},
        {"operation": "access_dict", "d": {"name": "김철수"}, "key": "age"},  # KeyError
    ]
    
    for case in test_cases:
        try:
            if case["operation"] == "divide":
                result = case["a"] / case["b"]
                print(f"[O] {case['a']} ÷ {case['b']} = {result}")
            
            elif case["operation"] == "access_list":
                value = case["lst"][case["index"]]
                print(f"[O] 리스트[{case['index']}] = {value}")
            
            elif case["operation"] == "access_dict":
                value = case["d"][case["key"]]
                print(f"[O] 딕셔너리['{case['key']}'] = {value}")
                
        except ZeroDivisionError:
            print(f"[X] 0으로 나눌 수 없습니다: {case['a']} ÷ {case['b']}")
        
        except IndexError:
            print(f"[X] 리스트 인덱스 범위 초과: {case['lst']}[{case['index']}]")
        
        except KeyError as e:
            print(f"[X] 딕셔너리에 키가 없습니다: {e}")
        
        except Exception as e:
            print(f"[X] 예상치 못한 오류: {type(e).__name__}: {e}")

def try_except_else_finally():
    """try-except-else-finally 구문"""
    
    print("\n3. try-except-else-finally 구문:")
    
    def process_file(filename: str, create_if_missing: bool = False):
        """파일 처리 함수"""
        file_handle = None
        
        try:
            print(f"파일 열기 시도: {filename}")
            
            file_handle = open(filename, "r", encoding="utf-8")
            
            print(f"[O] 파일 열기 성공: {filename}")
            
        except FileNotFoundError:
            print(f"[X] 파일을 찾을 수 없습니다: {filename}")
            if create_if_missing:
                try:
                    file_handle = open(filename, "w", encoding="utf-8")
                    file_handle.write(f"# {filename}\n생성 시간: {datetime.now()}\n")
                    print(f"[O] 새 파일 생성: {filename}")
                except Exception as create_error:
                    print(f"[X] 파일 생성 실패: {create_error}")
        
        except PermissionError:
            print(f"[X] 파일 접근 권한이 없습니다: {filename}")
        
        except Exception as e:
            print(f"[X] 예상치 못한 오류: {e}")
        
        else:
            # 예외가 발생하지 않았을 때만 실행
            print("[O] 파일 처리가 정상적으로 완료되었습니다")
            
            if file_handle and not file_handle.closed:
                if 'r' in file_handle.mode:
                    content = file_handle.read()
                    print(f"파일 내용 (첫 50자): {content[:50]}...")
        
        finally:
            # 항상 실행되는 블록
            if file_handle and not file_handle.closed:
                file_handle.close()
                print(f"파일 핸들 정리 완료: {filename}")
            print("--- 파일 처리 종료 ---\n")
    
    # 테스트 케이스들
    from datetime import datetime
    
    # 존재하지 않는 파일 (생성하지 않음)
    process_file("nonexistent.txt", create_if_missing=False)
    
    # 존재하지 않는 파일 (생성함)
    process_file("created_file.txt", create_if_missing=True)
    
    # 생성된 파일 읽기
    process_file("created_file.txt", create_if_missing=False)
    
    # 정리
    import os
    if os.path.exists("created_file.txt"):
        os.remove("created_file.txt")

def exception_information():
    """예외 정보 상세 확인"""
    
    print("\n4. 예외 정보 상세 확인:")
    
    def problematic_function():
        """의도적으로 오류를 발생시키는 함수"""
        data = {"한글": "Korean", "영어": "English"}
        
        # 여러 단계의 함수 호출
        def level1():
            return level2()
        
        def level2():
            return level3()
        
        def level3():
            # 의도적 오류 발생
            return data["중국어"]  # KeyError 발생
        
        return level1()
    
    try:
        result = problematic_function()
        print(f"결과: {result}")
        
    except KeyError as e:
        print(f"[X] KeyError 발생: {e}")
        print(f"예외 타입: {type(e)}")
        print(f"예외 메시지: {str(e)}")
        
        # 상세한 트레이스백 정보
        print("\n상세 트레이스백:")
        traceback.print_exc()
        
        # 트레이스백을 문자열로 저장
        trace_str = traceback.format_exc()
        print(f"\n트레이스백 문자열 길이: {len(trace_str)} 문자")
        
        # 스택 정보 분석
        import sys
        exc_type, exc_value, exc_traceback = sys.exc_info()
        
        print(f"\n예외 분석:")
        print(f"예외 타입: {exc_type.__name__}")
        print(f"예외 값: {exc_value}")
        
        # 스택 프레임 정보
        frames = traceback.extract_tb(exc_traceback)
        print(f"스택 프레임 수: {len(frames)}")
        
        for i, frame in enumerate(frames):
            print(f"  프레임 {i+1}: {frame.filename}:{frame.lineno} in {frame.name}")
            print(f"    코드: {frame.line}")

# 실행
print("=== 예외 처리 기본 ===")
basic_exception_handling()
multiple_exception_handling()
try_except_else_finally()
exception_information()
