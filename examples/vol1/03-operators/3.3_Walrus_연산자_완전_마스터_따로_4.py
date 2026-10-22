"""1권 Chapter 3. 연산과 표현식 — 3.3 Walrus 연산자 (:=) 완전 마스터

원고: manuscript/chapters/03-operators.md (359줄부터)
"""

# ---- 원고 359줄 ----
# 파일 읽기 패턴
def 파일_처리_기존방식(파일명):
    with open(파일명, 'r', encoding='utf-8') as f:
        line = f.readline()
        while line:
            print(f"처리 중: {line.strip()}")
            line = f.readline()  # 중복 코드

def 파일_처리_walrus(파일명):
    with open(파일명, 'r', encoding='utf-8') as f:
        while (line := f.readline()):  # 할당과 조건 검사 동시에
            print(f"처리 중: {line.strip()}")

# 사용자 입력 처리
def 사용자_입력_처리():
    명령들 = []
    while (명령 := input("명령을 입력하세요 (quit으로 종료): ")) != "quit":
        명령들.append(명령)
        print(f"'{명령}' 명령이 추가되었습니다.")
    
    return 명령들

# 네트워크 데이터 처리
import socket

def 데이터_수신_처리(소켓):
    받은_데이터들 = []
    while (데이터 := 소켓.recv(1024)):  # 데이터가 있는 동안
        받은_데이터들.append(데이터)
        if len(데이터) < 1024:  # 마지막 청크
            break
    return b''.join(받은_데이터들)
