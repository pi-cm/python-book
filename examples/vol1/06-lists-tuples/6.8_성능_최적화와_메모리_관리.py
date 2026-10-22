"""1권 Chapter 6: 리스트와 튜플 — 6.8 성능 최적화와 메모리 관리

원고: manuscript/chapters/06-lists-tuples.md (757줄부터)
"""

# ---- 원고 757줄 ----
import time

def performance_test():
    """리스트와 튜플의 성능 비교"""
    size = 1000000
    
    # 리스트 생성 시간
    start = time.time()
    test_list = list(range(size))
    list_creation_time = time.time() - start
    
    # 튜플 생성 시간
    start = time.time()
    test_tuple = tuple(range(size))
    tuple_creation_time = time.time() - start
    
    # 인덱스 접근 시간 (리스트)
    start = time.time()
    for _ in range(1000):
        _ = test_list[size // 2]
    list_access_time = time.time() - start
    
    # 인덱스 접근 시간 (튜플)
    start = time.time()
    for _ in range(1000):
        _ = test_tuple[size // 2]
    tuple_access_time = time.time() - start
    
    print("성능 비교 결과:")
    print(f"리스트 생성: {list_creation_time:.6f}초")
    print(f"튜플 생성: {tuple_creation_time:.6f}초")
    print(f"리스트 접근: {list_access_time:.6f}초")
    print(f"튜플 접근: {tuple_access_time:.6f}초")

# 성능 테스트 실행 (주석 해제 시 실행)
# performance_test()

# ---- 원고 800줄 ----
import sys

def memory_comparison():
    """메모리 사용량 비교"""
    # 일반 리스트
    normal_list = [i for i in range(1000)]
    
    # 제너레이터 표현식
    generator_expr = (i for i in range(1000))
    
    # 튜플
    tuple_data = tuple(range(1000))
    
    print("메모리 사용량 비교:")
    print(f"리스트: {sys.getsizeof(normal_list)} bytes")
    print(f"제너레이터: {sys.getsizeof(generator_expr)} bytes")
    print(f"튜플: {sys.getsizeof(tuple_data)} bytes")

# 대용량 데이터 처리 최적화
def process_large_dataset(data):
    """대용량 데이터 효율적 처리"""
    # 나쁜 예: 모든 데이터를 메모리에 로드
    # result = [process_item(item) for item in data]
    
    # 좋은 예: 제너레이터 사용
    def process_items():
        for item in data:
            yield process_item(item)
    
    return process_items()

def process_item(item):
    """개별 아이템 처리 (예제)"""
    return item * 2

# 청크 단위 처리
def process_in_chunks(data, chunk_size=1000):
    """데이터를 청크 단위로 처리"""
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        yield [process_item(item) for item in chunk]

# 메모리 비교 실행
memory_comparison()
