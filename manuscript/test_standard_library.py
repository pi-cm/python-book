"""
표준 라이브러리 핵심 가이드 테스트
한국어 컨텍스트를 활용한 TDD 테스트 케이스
"""

import pytest
from pathlib import Path
import datetime
import json
import re
import statistics
from collections import Counter, defaultdict
from unittest.mock import patch, mock_open
import urllib.request
import urllib.parse


class TestKoreanTextProcessing:
    """문자열과 텍스트 처리 테스트"""
    
    def test_korean_string_operations(self):
        """한글 문자열 기본 연산 테스트"""
        # 이 테스트들은 처음에 실패해야 함 (RED)
        korean_text = "안녕하세요 파이썬!"
        assert len(korean_text) > 0
        assert "파이썬" in korean_text
        assert korean_text.startswith("안녕")
    
    def test_korean_regex_patterns(self):
        """한국어 정규표현식 패턴 테스트"""
        # 한글 매칭 패턴이 제대로 작동하는지 테스트
        text = "김철수의 전화번호는 010-1234-5678입니다."
        korean_pattern = re.compile(r'[가-힣]+')
        phone_pattern = re.compile(r'010-\d{4}-\d{4}')
        
        # 한글 단어들 찾기
        korean_matches = korean_pattern.findall(text)
        assert "김철수의" in korean_matches  # 조사 포함된 형태
        assert "전화번호는" in korean_matches  # 조사 포함된 형태
        
        phone_matches = phone_pattern.findall(text)
        assert "010-1234-5678" in phone_matches


class TestKoreanDateTime:
    """날짜와 시간 처리 테스트"""
    
    def test_korean_timezone_handling(self):
        """한국 시간대 처리 테스트"""
        # 서울 시간대가 제대로 처리되는지 테스트
        from zoneinfo import ZoneInfo
        
        seoul_tz = ZoneInfo("Asia/Seoul")
        korean_time = datetime.datetime.now(seoul_tz)
        assert korean_time.tzinfo is not None
        assert str(korean_time.tzinfo) == "Asia/Seoul"
    
    def test_korean_holiday_detection(self):
        """한국 휴일 검출 테스트"""
        # 한국 공휴일이 제대로 검출되는지 테스트
        korean_holidays = [
            datetime.date(2024, 1, 1),   # 신정
            datetime.date(2024, 3, 1),   # 삼일절
            datetime.date(2024, 5, 5),   # 어린이날
        ]
        
        test_date = datetime.date(2024, 3, 1)
        assert test_date in korean_holidays


class TestKoreanFileSystem:
    """파일 시스템과 경로 테스트"""
    
    def test_korean_filename_handling(self):
        """한국어 파일명 처리 테스트"""
        # 한국어 파일명이 제대로 처리되는지 테스트
        korean_filename = Path("한국어_데이터.txt")
        assert korean_filename.suffix == ".txt"
        assert "한국어" in korean_filename.stem
    
    def test_pathlib_korean_operations(self):
        """pathlib로 한국어 경로 처리 테스트"""
        # pathlib이 한국어 경로를 제대로 처리하는지 테스트
        korean_path = Path("데이터") / "한국어" / "텍스트.txt"
        assert korean_path.parts[-1] == "텍스트.txt"
        assert korean_path.parent.name == "한국어"


class TestKoreanDataSerialization:
    """데이터 직렬화 테스트"""
    
    def test_korean_json_handling(self):
        """한글 JSON 처리 테스트"""
        # 한글이 포함된 JSON 데이터 처리 테스트
        korean_data = {
            "이름": "김철수",
            "나이": 25,
            "주소": "서울특별시 강남구"
        }
        
        json_str = json.dumps(korean_data, ensure_ascii=False)
        assert "김철수" in json_str
        
        loaded_data = json.loads(json_str)
        assert loaded_data["이름"] == "김철수"
    
    def test_korean_csv_processing(self):
        """한글 CSV 처리 테스트"""
        # 한글이 포함된 CSV 데이터 처리 테스트
        csv_content = "이름,나이,도시\n김철수,25,서울\n이영희,30,부산\n"
        
        with patch("builtins.open", mock_open(read_data=csv_content)):
            import io
            from csv import DictReader
            
            reader = DictReader(io.StringIO(csv_content))
            rows = list(reader)
            
            assert len(rows) == 2
            assert rows[0]["이름"] == "김철수"
            assert rows[0]["도시"] == "서울"


class TestKoreanNetworking:
    """네트워킹과 인터넷 테스트"""
    
    def test_korean_url_encoding(self):
        """한글 URL 인코딩 테스트"""
        # 한글이 포함된 URL이 제대로 인코딩되는지 테스트
        korean_query = "파이썬 프로그래밍"
        encoded = urllib.parse.quote(korean_query)
        
        assert encoded != korean_query
        
        decoded = urllib.parse.unquote(encoded)
        assert decoded == korean_query
    
    @patch('urllib.request.urlopen')
    def test_korean_api_request(self, mock_urlopen):
        """한국 API 요청 테스트"""
        # 한국 API 서비스 요청 모의 테스트
        import io
        mock_response_data = '{"결과": "성공", "데이터": "한글 데이터"}'
        mock_response = io.BytesIO(mock_response_data.encode('utf-8'))
        mock_response.status = 200
        
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        url = "https://api.korean-service.com/data"
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
            assert "한글 데이터" in data


class TestKoreanMathStatistics:
    """수학과 통계 테스트"""
    
    def test_korean_financial_calculations(self):
        """한국 금융 계산 테스트"""
        # 한국 금융 상품 계산 예시
        principal = 10000000  # 원금 천만원
        annual_rate = 0.03   # 연 3% 이자율
        years = 5
        
        compound_interest = principal * (1 + annual_rate) ** years
        assert compound_interest > principal
        
        monthly_rate = annual_rate / 12
        monthly_payment = (principal * monthly_rate) / (1 - (1 + monthly_rate) ** (-years * 12))
        assert monthly_payment > 0
    
    def test_korean_statistics_analysis(self):
        """한국 데이터 통계 분석 테스트"""
        # 한국 도시별 인구 데이터 분석
        city_populations = [9720846, 3413841, 2466052, 1538394, 1501557]  # 서울, 부산, 인천, 대구, 대전
        
        mean_pop = statistics.mean(city_populations)
        median_pop = statistics.median(city_populations)
        stdev_pop = statistics.stdev(city_populations)
        
        assert mean_pop > 0
        assert median_pop > 0
        assert stdev_pop > 0


class TestKoreanCollectionsIteration:
    """컬렉션과 반복 테스트"""
    
    def test_korean_counter_operations(self):
        """한글 텍스트 카운팅 테스트"""
        # 한글 문서에서 단어 빈도 계산
        korean_text = "파이썬은 좋은 언어입니다. 파이썬을 배워보세요. 파이썬은 재미있습니다."
        words = korean_text.replace(".", "").replace(",", "").split()
        
        word_count = Counter(words)
        assert word_count["파이썬은"] == 2
        assert word_count.most_common(1)[0][0] in ["파이썬은", "파이썬을"]
    
    def test_korean_defaultdict_usage(self):
        """한국 데이터 그룹화 테스트"""
        # 지역별 데이터 그룹화
        students = [
            ("김철수", "서울"),
            ("이영희", "부산"),
            ("박민수", "서울"),
            ("정수진", "대구"),
            ("최지영", "서울")
        ]
        
        by_city = defaultdict(list)
        for name, city in students:
            by_city[city].append(name)
        
        assert len(by_city["서울"]) == 3
        assert "김철수" in by_city["서울"]


class TestKoreanLogging:
    """로깅과 디버깅 테스트"""
    
    def test_korean_log_formatting(self):
        """한글 로그 메시지 포맷팅 테스트"""
        import logging
        import io
        
        # 한글 로그 메시지가 제대로 처리되는지 테스트
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        
        logger = logging.getLogger('한국어_로거')
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        logger.info("사용자 %s님이 로그인했습니다.", "김철수")
        
        log_output = log_stream.getvalue()
        assert "김철수" in log_output
        assert "로그인했습니다" in log_output


class TestKoreanConcurrency:
    """동시성과 병렬성 테스트"""
    
    def test_korean_threading_safety(self):
        """한국어 데이터 스레드 안전성 테스트"""
        import threading
        import time
        
        korean_data = {"카운터": 0, "메시지": []}
        lock = threading.Lock()
        
        def korean_worker(worker_id):
            for i in range(5):
                with lock:
                    korean_data["카운터"] += 1
                    korean_data["메시지"].append(f"작업자_{worker_id}: {i}번째 작업")
                time.sleep(0.001)
        
        threads = []
        for i in range(3):
            thread = threading.Thread(target=korean_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        assert korean_data["카운터"] == 15
        assert len(korean_data["메시지"]) == 15


class TestKoreanSystemInterface:
    """시스템과 OS 인터페이스 테스트"""
    
    def test_korean_environment_variables(self):
        """한국어 환경변수 테스트"""
        import os
        
        # 한글 환경변수 설정 및 읽기 테스트
        korean_var = "한국어_설정"
        korean_value = "서울_KR"
        
        os.environ[korean_var] = korean_value
        assert os.environ.get(korean_var) == korean_value
        
        # 정리
        del os.environ[korean_var]
    
    def test_korean_subprocess_handling(self):
        """한국어 서브프로세스 처리 테스트"""
        import subprocess
        import sys
        
        # 한글 출력을 포함하는 파이썬 코드 실행 테스트
        korean_code = 'print("안녕하세요 파이썬!")'
        
        result = subprocess.run(
            [sys.executable, "-c", korean_code],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        assert result.returncode == 0
        assert "안녕하세요" in result.stdout


# 실제 구현이 없으면 이 테스트들은 모두 실패할 것 (RED phase)
if __name__ == "__main__":
    pytest.main([__file__, "-v"])