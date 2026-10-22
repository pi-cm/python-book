"""1권 Chapter 7: 딕셔너리와 집합 — 7.6 딕셔너리와 집합의 성능

원고: manuscript/chapters/07-dictionaries-sets.md (456줄부터)
"""

# ---- 원고 456줄 ----
import timeit

def performance_comparison():
    """딕셔너리/집합 vs 리스트 성능 비교"""
    # 테스트 데이터 생성
    size = 100000
    test_data = list(range(size))
    test_list = test_data.copy()
    test_set = set(test_data)
    test_dict = {i: f"값_{i}" for i in test_data}
    
    search_target = size - 1  # 마지막 요소 검색
    repeat = 200  # 한 번만 재면 너무 짧아 0초로 찍히므로 여러 번 재서 평균을 낸다
    
    # 리스트에서 검색 (O(n))
    list_search_time = timeit.timeit(lambda: search_target in test_list, number=repeat) / repeat
    
    # 집합에서 검색 (O(1) 평균)
    set_search_time = timeit.timeit(lambda: search_target in test_set, number=repeat) / repeat
    
    # 딕셔너리에서 검색 (O(1) 평균)
    dict_search_time = timeit.timeit(lambda: search_target in test_dict, number=repeat) / repeat
    
    print("검색 성능 비교 (10만 개 요소, 1회 평균):")
    print(f"리스트 검색: {list_search_time:.9f}초")
    print(f"집합 검색:   {set_search_time:.9f}초")
    print(f"딕셔너리 검색: {dict_search_time:.9f}초")
    print(f"집합이 리스트보다 {list_search_time/set_search_time:,.0f}배 빠름")

# 성능 테스트 실행 (주석 해제 시)
# performance_comparison()

# ---- 원고 497줄 ----
import sys

def memory_analysis():
    """자료구조별 메모리 사용량 분석"""
    size = 1000
    
    # 같은 데이터를 다른 구조로 저장
    test_list = list(range(size))
    test_tuple = tuple(range(size))
    test_set = set(range(size))
    test_dict = {i: i for i in range(size)}
    
    print("메모리 사용량 비교 (1000개 요소):")
    print(f"리스트:     {sys.getsizeof(test_list):5} bytes")
    print(f"튜플:       {sys.getsizeof(test_tuple):5} bytes") 
    print(f"집합:       {sys.getsizeof(test_set):5} bytes")
    print(f"딕셔너리:   {sys.getsizeof(test_dict):5} bytes")
    
    # 용도별 권장사항
    print("\n용도별 권장사항:")
    print("- 순서가 중요하고 중복 허용: 리스트")
    print("- 불변이고 순서 중요: 튜플")  
    print("- 중복 없는 고유값, 빠른 검색: 집합")
    print("- 키-값 매핑, 빠른 조회: 딕셔너리")

memory_analysis()
