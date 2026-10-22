"""1권 Chapter 12: 파일과 예외 처리 — 12.1 파일 입출력 기본

원고: manuscript/chapters/12-files-exceptions.md (31줄부터)
"""

# ---- 원고 31줄 ----
# 전통적인 파일 처리 방식
def traditional_file_handling():
    """전통적인 파일 처리"""
    # 파일 쓰기
    file = open("korean_greeting.txt", "w", encoding="utf-8")
    file.write("안녕하세요!\n")
    file.write("파이썬 파일 처리를 배우고 있습니다.\n")
    file.close()
    
    # 파일 읽기
    file = open("korean_greeting.txt", "r", encoding="utf-8")
    content = file.read()
    file.close()
    
    print("파일 내용:")
    print(content)

# 현대적인 파일 처리 방식 (권장)
def modern_file_handling():
    """컨텍스트 매니저를 사용한 현대적 파일 처리"""
    
    # 파일 쓰기
    with open("korean_modern.txt", "w", encoding="utf-8") as file:
        file.write("파이썬으로 한글 파일 처리하기\n")
        file.write("=" * 30 + "\n")
        
        korean_data = [
            "이름: 김철수",
            "나이: 25세", 
            "직업: 소프트웨어 개발자",
            "관심사: 파이썬, 데이터 분석, 웹 개발"
        ]
        
        for line in korean_data:
            file.write(f"{line}\n")
    
    # 파일 읽기 (전체)
    with open("korean_modern.txt", "r", encoding="utf-8") as file:
        content = file.read()
        print("전체 파일 내용:")
        print(content)
    
    # 파일 읽기 (줄별)
    print("\n줄별 읽기:")
    with open("korean_modern.txt", "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, 1):
            print(f"줄 {line_number}: {line.strip()}")

# 다양한 파일 읽기 방법
def various_reading_methods():
    """다양한 파일 읽기 방법 시연"""
    
    # 테스트 파일 생성
    test_content = """첫 번째 줄입니다.
두 번째 줄에는 한글이 있습니다.
세 번째 줄: 숫자 12345
네 번째 줄: 특수문자 !@#$%
다섯 번째 줄입니다."""
    
    with open("test_reading.txt", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    print("1. read() - 전체 내용:")
    with open("test_reading.txt", "r", encoding="utf-8") as f:
        content = f.read()
        print(repr(content))
    
    print("\n2. readline() - 한 줄씩:")
    with open("test_reading.txt", "r", encoding="utf-8") as f:
        line_count = 0
        while True:
            line = f.readline()
            if not line:  # 파일 끝
                break
            line_count += 1
            print(f"줄 {line_count}: {repr(line)}")
    
    print("\n3. readlines() - 모든 줄을 리스트로:")
    with open("test_reading.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        for i, line in enumerate(lines, 1):
            print(f"줄 {i}: {repr(line)}")
    
    print("\n4. 이터레이터 방식 (권장):")
    with open("test_reading.txt", "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            print(f"줄 {i}: {line.strip()}")

# 한글 인코딩 처리
def korean_encoding_demo():
    """한글 인코딩 처리 시연"""
    
    korean_text = """안녕하세요! 
한글 인코딩 테스트입니다.
UTF-8: 유니코드 표준 인코딩
CP949: 윈도우 한글 인코딩
EUC-KR: 구 한글 인코딩"""
    
    # UTF-8로 저장 (권장)
    with open("korean_utf8.txt", "w", encoding="utf-8") as f:
        f.write(korean_text)
    
    # CP949로 저장 (윈도우 호환용)
    with open("korean_cp949.txt", "w", encoding="cp949") as f:
        f.write(korean_text)
    
    print("인코딩별 파일 크기:")
    import os
    utf8_size = os.path.getsize("korean_utf8.txt")
    cp949_size = os.path.getsize("korean_cp949.txt")
    
    print(f"UTF-8: {utf8_size} bytes")
    print(f"CP949: {cp949_size} bytes")
    
    # 잘못된 인코딩으로 읽기 시도
    print("\n인코딩 오류 시연:")
    try:
        with open("korean_utf8.txt", "r", encoding="ascii") as f:
            content = f.read()
    except UnicodeDecodeError as e:
        print(f"[X] ASCII로 UTF-8 파일 읽기 실패: {e}")
    
    # 올바른 인코딩으로 읽기
    with open("korean_utf8.txt", "r", encoding="utf-8") as f:
        content = f.read()
        print(f"[O] UTF-8로 올바르게 읽음:\n{content}")

# 실행
print("=== 전통적인 파일 처리 ===")
traditional_file_handling()

print("\n=== 현대적인 파일 처리 ===")
modern_file_handling()

print("\n=== 다양한 읽기 방법 ===")
various_reading_methods()

print("\n=== 한글 인코딩 처리 ===")
korean_encoding_demo()

# ---- 원고 179줄 ----
for text in ["A", "가", "漢"]:
    print(text, len(text.encode("utf-8")), len(text.encode("cp949")))
# A 1 1
# 가 3 2
# 漢 3 2

# ---- 원고 206줄 ----
import os
from pathlib import Path

def file_modes_demo():
    """파일 모드 시연"""
    
    test_file = "mode_test.txt"
    
    # 1. 'w' 모드: 쓰기 (기존 파일 덮어쓰기)
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("첫 번째 내용\n")
    
    # 2. 'a' 모드: 추가 (기존 파일 끝에 추가)
    with open(test_file, "a", encoding="utf-8") as f:
        f.write("두 번째 내용 (추가)\n")
        f.write("세 번째 내용 (추가)\n")
    
    # 3. 'r' 모드: 읽기 (기본값)
    with open(test_file, "r", encoding="utf-8") as f:
        content = f.read()
        print(f"'a' 모드 후 파일 내용:\n{content}")
    
    # 4. 'x' 모드: 배타적 생성 (파일이 이미 있으면 오류)
    exclusive_file = "exclusive_test.txt"
    
    try:
        with open(exclusive_file, "x", encoding="utf-8") as f:
            f.write("배타적 생성 모드 테스트\n")
        print("[O] 'x' 모드로 새 파일 생성 성공")
    except FileExistsError:
        print("[X] 'x' 모드: 파일이 이미 존재함")
    
    # 같은 파일을 다시 'x' 모드로 열려고 시도
    try:
        with open(exclusive_file, "x", encoding="utf-8") as f:
            f.write("이 내용은 쓰여지지 않음\n")
    except FileExistsError:
        print("[X] 'x' 모드: 기존 파일이 있어서 실패")
    
    # 5. 'r+' 모드: 읽기/쓰기
    with open(test_file, "r+", encoding="utf-8") as f:
        # 파일 시작 부분에서 읽기
        original_content = f.read()
        print(f"'r+' 모드 - 원본 내용:\n{original_content}")
        
        # 파일 끝에 추가
        f.write("네 번째 내용 (r+ 모드)\n")
    
    # 6. 'w+' 모드: 읽기/쓰기 (기존 파일 덮어쓰기)
    with open("rw_test.txt", "w+", encoding="utf-8") as f:
        f.write("w+ 모드 테스트\n")
        f.write("읽기와 쓰기 모두 가능\n")
        
        # 파일 포인터를 시작으로 이동
        f.seek(0)
        content = f.read()
        print(f"'w+' 모드로 쓴 후 읽기:\n{content}")
    
    # 정리
    for file in [test_file, exclusive_file, "rw_test.txt"]:
        if os.path.exists(file):
            os.remove(file)

def binary_file_demo():
    """바이너리 파일 처리 시연"""
    
    # 바이너리 데이터 생성 (간단한 이미지 데이터 시뮬레이션)
    binary_data = bytes([0xFF, 0xD8, 0xFF, 0xE0] + list(range(100)))
    
    # 바이너리 쓰기
    with open("test_binary.dat", "wb") as f:
        f.write(binary_data)
        f.write(b"\x00\x01\x02\x03")  # 추가 바이너리 데이터
    
    # 바이너리 읽기
    with open("test_binary.dat", "rb") as f:
        read_data = f.read()
        print(f"바이너리 파일 크기: {len(read_data)} bytes")
        print(f"첫 10바이트: {read_data[:10]}")
        print(f"마지막 4바이트: {read_data[-4:]}")
    
    # 바이너리와 텍스트 혼합 처리
    mixed_data = {
        "header": "한글 헤더 정보",
        "binary_data": binary_data,
        "footer": "푸터 정보"
    }
    
    # 텍스트 부분은 UTF-8, 바이너리는 그대로
    with open("mixed_data.bin", "wb") as f:
        # 헤더 쓰기 (UTF-8 인코딩)
        header_bytes = mixed_data["header"].encode("utf-8")
        f.write(len(header_bytes).to_bytes(4, byteorder='big'))  # 헤더 길이 (4바이트)
        f.write(header_bytes)
        
        # 바이너리 데이터 쓰기
        f.write(len(mixed_data["binary_data"]).to_bytes(4, byteorder='big'))  # 데이터 길이
        f.write(mixed_data["binary_data"])
        
        # 푸터 쓰기
        footer_bytes = mixed_data["footer"].encode("utf-8")
        f.write(len(footer_bytes).to_bytes(4, byteorder='big'))  # 푸터 길이
        f.write(footer_bytes)
    
    # 혼합 데이터 읽기
    with open("mixed_data.bin", "rb") as f:
        # 헤더 읽기
        header_length = int.from_bytes(f.read(4), byteorder='big')
        header = f.read(header_length).decode("utf-8")
        
        # 바이너리 데이터 읽기  
        data_length = int.from_bytes(f.read(4), byteorder='big')
        binary_data = f.read(data_length)
        
        # 푸터 읽기
        footer_length = int.from_bytes(f.read(4), byteorder='big')
        footer = f.read(footer_length).decode("utf-8")
        
        print(f"\n혼합 파일 읽기 결과:")
        print(f"헤더: {header}")
        print(f"바이너리 데이터 크기: {len(binary_data)} bytes")
        print(f"푸터: {footer}")
    
    # 정리
    for file in ["test_binary.dat", "mixed_data.bin"]:
        if os.path.exists(file):
            os.remove(file)

# 실행
print("=== 파일 모드 시연 ===")
file_modes_demo()

print("\n=== 바이너리 파일 처리 ===")
binary_file_demo()
