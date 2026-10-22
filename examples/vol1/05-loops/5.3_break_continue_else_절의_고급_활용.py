"""1권 Chapter 5. 반복문과 루프 — 5.3 break, continue, else 절의 고급 활용

원고: manuscript/chapters/05-loops.md (441줄부터)
"""

# ---- 원고 441줄 ----
for i in range(20):
    print(f"{i}: 시작")
    if i < 2:
        pass        # 아무 일 없이 아래로 계속
    elif i < 4:
        continue    # 아래 "끝"을 건너뛰고 다음 i로
    else:
        break       # 반복 전체를 끝냄
    print(f"{i}: 끝")

# ---- 원고 457줄 ----
# 1. break를 활용한 조기 종료
def 소수_찾기(최대값):
    """지정된 범위에서 소수 찾기 (break 활용)"""
    소수들 = []
    
    for 숫자 in range(2, 최대값 + 1):
        소수인가 = True
        
        # 2부터 숫자의 제곱근까지만 확인 (최적화)
        for 나누는_수 in range(2, int(숫자 ** 0.5) + 1):
            if 숫자 % 나누는_수 == 0:
                소수인가 = False
                break  # 소수가 아니면 더 이상 확인할 필요 없음
        
        if 소수인가:
            소수들.append(숫자)
    
    return 소수들

print("=== break 활용: 소수 찾기 ===")
소수_목록 = 소수_찾기(30)
print(f"30 이하의 소수: {소수_목록}")

# 2. continue를 활용한 선택적 처리
def 한국어_텍스트_필터링(텍스트_목록):
    """한국어가 포함된 텍스트만 처리 (continue 활용)"""
    처리된_텍스트들 = []
    
    for 텍스트 in 텍스트_목록:
        # 빈 문자열 건너뛰기
        if not 텍스트.strip():
            continue
        
        # 한국어 문자가 없으면 건너뛰기
        한국어_포함 = any('\uac00' <= 문자 <= '\ud7a3' for 문자 in 텍스트)
        if not 한국어_포함:
            continue
        
        # 너무 짧거나 긴 텍스트 건너뛰기
        if len(텍스트) < 2 or len(텍스트) > 100:
            continue
        
        # 모든 조건을 통과한 텍스트만 처리
        처리된_텍스트 = 텍스트.strip().upper()
        처리된_텍스트들.append(처리된_텍스트)
    
    return 처리된_텍스트들

텍스트_예제들 = [
    "안녕하세요",
    "",
    "Hello World",
    "파이썬 프로그래밍",
    "Python",
    "한국어와 English 혼합",
    "가"
]

print("\n=== continue 활용: 한국어 텍스트 필터링 ===")
print(f"원본 텍스트: {텍스트_예제들}")
필터링_결과 = 한국어_텍스트_필터링(텍스트_예제들)
print(f"필터링 결과: {필터링_결과}")

# 3. 중첩 루프에서 break/continue
def 구구단_선택적_출력(시작단=2, 끝단=9):
    """특정 조건의 구구단만 출력"""
    print("=== 선택적 구구단 출력 ===")
    
    for 단 in range(시작단, 끝단 + 1):
        # 홀수 단만 출력
        if 단 % 2 == 0:
            continue
        
        print(f"\n{단}단:")
        
        for 곱 in range(1, 10):
            결과 = 단 * 곱
            
            # 결과가 50 이상이면 해당 단 중단
            if 결과 >= 50:
                print(f"  (50 이상이므로 {단}단 중단)")
                break
            
            print(f"  {단} × {곱} = {결과}")

구구단_선택적_출력()

# ---- 원고 557줄 ----
# 1. 비교용: break가 없으면 else도 필요 없다
def 완전수_찾기(최대값):
    """완전수 찾기 (안쪽 반복에 break가 없으므로 else 없이 쓴다)"""
    완전수들 = []
    
    for 숫자 in range(1, 최대값 + 1):
        약수_합 = 0
        
        # 자기 자신을 제외한 약수들의 합 계산
        for 나누는_수 in range(1, 숫자):
            if 숫자 % 나누는_수 == 0:
                약수_합 += 나누는_수
        
        # 안쪽 반복이 다 끝난 뒤 약수의 합을 확인
        if 약수_합 == 숫자:
            완전수들.append(숫자)
    
    return 완전수들

print("=== 완전수 찾기 ===")
완전수_목록 = 완전수_찾기(30)
print(f"30 이하의 완전수: {완전수_목록}")

# 2. while-else: 조건으로 종료된 경우
def 타겟_찾기(리스트, 타겟):
    """리스트에서 타겟 값 찾기 (while-else 활용)"""
    인덱스 = 0
    
    while 인덱스 < len(리스트):
        if 리스트[인덱스] == 타겟:
            print(f"타겟 '{타겟}'을 인덱스 {인덱스}에서 발견!")
            break
        인덱스 += 1
    else:
        # while 조건이 False가 되어 종료됨 (break로 종료되지 않음)
        print(f"타겟 '{타겟}'을 찾지 못했습니다.")
    
    return 인덱스 if 인덱스 < len(리스트) else -1

한국_도시들 = ["서울", "부산", "대구", "인천", "광주", "대전", "울산"]

print("\n=== while-else 활용: 타겟 찾기 ===")
타겟_찾기(한국_도시들, "광주")  # 찾을 수 있는 경우
타겟_찾기(한국_도시들, "제주")  # 찾을 수 없는 경우

# 3. 복잡한 조건에서 else 절 활용
def 소수_판별_with_else(숫자):
    """소수 판별 (else 절로 결과 처리)"""
    if 숫자 < 2:
        return False
    
    for 나누는_수 in range(2, int(숫자 ** 0.5) + 1):
        if 숫자 % 나누는_수 == 0:
            print(f"{숫자}는 {나누는_수}로 나누어지므로 소수가 아닙니다.")
            break
    else:
        # for 루프가 break 없이 끝남 = 소수임
        print(f"{숫자}는 소수입니다!")
        return True
    
    return False

print("\n=== for-else 활용: 소수 판별 ===")
테스트_숫자들 = [17, 21, 23, 25, 29]
for 숫자 in 테스트_숫자들:
    소수_판별_with_else(숫자)
