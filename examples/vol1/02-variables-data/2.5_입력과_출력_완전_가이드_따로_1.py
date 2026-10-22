"""1권 Chapter 2. 변수와 데이터 — 2.5 입력과 출력 완전 가이드

원고: manuscript/chapters/02-variables-data.md (714줄부터)
"""

# ---- 원고 714줄 ----
def 안전한_입력():
    """타입 안전한 입력 함수들"""
    
    def 정수_입력(메시지: str, 최소값: int = None, 최대값: int = None) -> int:
        while True:
            try:
                값 = int(input(메시지))
                if 최소값 is not None and 값 < 최소값:
                    print(f"값은 {최소값} 이상이어야 합니다.")
                    continue
                if 최대값 is not None and 값 > 최대값:
                    print(f"값은 {최대값} 이하여야 합니다.")
                    continue
                return 값
            except ValueError:
                print("올바른 정수를 입력해주세요.")
    
    def 실수_입력(메시지: str) -> float:
        while True:
            try:
                return float(input(메시지))
            except ValueError:
                print("올바른 실수를 입력해주세요.")
    
    def 선택_입력(메시지: str, 선택지: list) -> str:
        while True:
            선택 = input(f"{메시지} {선택지}: ")
            if 선택 in 선택지:
                return 선택
            print(f"다음 중 하나를 선택해주세요: {선택지}")
    
    # 사용 예제
    print("=== 안전한 입력 예제 ===")
    이름 = input("이름을 입력하세요: ")
    나이 = 정수_입력("나이를 입력하세요 (1-120): ", 1, 120)
    키 = 실수_입력("키를 입력하세요 (cm): ")
    성별 = 선택_입력("성별을 선택하세요", ["남", "여"])
    
    return {
        "이름": 이름,
        "나이": 나이,
        "키": 키,
        "성별": 성별
    }

# 실행 예제 (실제로는 사용자 입력을 받음)
# 정보 = 안전한_입력()
# print(f"입력받은 정보: {정보}")
