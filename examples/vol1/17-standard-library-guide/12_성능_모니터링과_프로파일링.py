"""1권 Chapter 17: 표준 라이브러리 핵심 가이드 — 성능 모니터링과 프로파일링

원고: manuscript/chapters/17-standard-library-guide.md (1658줄부터)
"""

# ---- 원고 1658줄 ----
import cProfile
import pstats
import memory_profiler
import time
from functools import wraps
from typing import Callable

class KoreanPerformanceMonitor:
    """한국어 성능 모니터링 시스템"""
    
    def __init__(self):
        self.metrics = {}
    
    def profile_function(self, func: Callable):
        """함수 프로파일링 데코레이터"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            # CPU 프로파일링
            profiler = cProfile.Profile()
            profiler.enable()
            
            # 메모리 사용량 측정 시작
            start_memory = memory_profiler.memory_usage()[0]
            start_time = time.perf_counter()
            
            try:
                result = func(*args, **kwargs)
                
                # 측정 종료
                end_time = time.perf_counter()
                end_memory = memory_profiler.memory_usage()[0]
                profiler.disable()
                
                # 결과 저장
                function_name = func.__name__
                self.metrics[function_name] = {
                    'execution_time': end_time - start_time,
                    'memory_delta': end_memory - start_memory,
                    'memory_peak': max(memory_profiler.memory_usage()),
                    'call_count': self.metrics.get(function_name, {}).get('call_count', 0) + 1
                }
                
                # 프로파일 결과 저장
                stats = pstats.Stats(profiler)
                stats.sort_stats('cumulative')
                
                print(f"\n=== {function_name} 성능 리포트 ===")
                print(f"실행시간: {end_time - start_time:.4f}초")
                print(f"메모리 변화: {end_memory - start_memory:.2f}MB")
                print(f"호출 횟수: {self.metrics[function_name]['call_count']}")
                
                return result
                
            except Exception as e:
                profiler.disable()
                print(f"함수 {function_name} 실행 중 오류 발생: {e}")
                raise
        
        return wrapper
    
    def get_performance_summary(self) -> dict:
        """성능 요약 정보 반환"""
        if not self.metrics:
            return {"message": "수집된 성능 데이터가 없습니다"}
        
        summary = {}
        for func_name, metrics in self.metrics.items():
            summary[func_name] = {
                'average_time': metrics['execution_time'] / metrics['call_count'],
                'total_time': metrics['execution_time'],
                'call_count': metrics['call_count'],
                'memory_usage': metrics['memory_delta']
            }
        
        return summary

# 전역 성능 모니터
performance_monitor = KoreanPerformanceMonitor()

@performance_monitor.profile_function
def process_large_korean_dataset():
    """대용량 한국어 데이터 처리 시뮬레이션"""
    korean_words = ["안녕", "하세요", "파이썬", "프로그래밍"] * 100000
    
    # CPU 집약적 작업
    result = []
    for word in korean_words:
        processed = word.upper() + "_처리됨"
        result.append(processed)
    
    # 메모리 집약적 작업
    large_dict = {f"키_{i}": f"한글_값_{i}" for i in range(50000)}
    
    return len(result), len(large_dict)

# 성능 테스트 실행
# result = process_large_korean_dataset()
# summary = performance_monitor.get_performance_summary()
# print("\n전체 성능 요약:", summary)
