"""1권 Chapter 17: 표준 라이브러리 핵심 가이드 — 동시성과 병렬성

원고: manuscript/chapters/17-standard-library-guide.md (909줄부터)
"""

# ---- 원고 909줄 ----
import threading
import time
import queue

# 한국어 채팅 서버 시뮬레이션
class KoreanChatServer:
    def __init__(self):
        self.messages = queue.Queue()
        self.clients = []
        self.running = True
    
    def add_client(self, name):
        self.clients.append(name)
        print(f"{name}님이 채팅방에 입장했습니다")
    
    def send_message(self, sender, message):
        self.messages.put(f"{sender}: {message}")
    
    def broadcast_worker(self):
        """메시지 브로드캐스트 워커 스레드"""
        while self.running:
            try:
                message = self.messages.get(timeout=1)
                print(f"[전체 메시지] {message}")
                self.messages.task_done()
            except queue.Empty:
                continue

# 채팅 서버 테스트
chat_server = KoreanChatServer()

# 브로드캐스트 스레드 시작
broadcast_thread = threading.Thread(target=chat_server.broadcast_worker)
broadcast_thread.daemon = True
broadcast_thread.start()

# 클라이언트들 추가
chat_server.add_client("김철수")
chat_server.add_client("이영희")
chat_server.add_client("박민수")

# 메시지 전송 시뮬레이션
def client_worker(server, name, messages):
    for msg in messages:
        time.sleep(0.5)
        server.send_message(name, msg)

# 여러 클라이언트가 동시에 메시지 전송
clients_threads = [
    threading.Thread(target=client_worker, args=(
        chat_server, "김철수", ["안녕하세요!", "오늘 날씨가 좋네요"]
    )),
    threading.Thread(target=client_worker, args=(
        chat_server, "이영희", ["네, 안녕하세요!", "정말 그렇네요"]
    )),
    threading.Thread(target=client_worker, args=(
        chat_server, "박민수", ["반갑습니다", "좋은 하루 되세요"]
    ))
]

for thread in clients_threads:
    thread.start()

for thread in clients_threads:
    thread.join()

# 정리
time.sleep(2)
chat_server.running = False

# ---- 원고 989줄 ----
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time

# 한국 뉴스 사이트들에서 데이터 수집 (시뮬레이션)
korean_news_sites = [
    "https://news.naver.com",
    "https://news.daum.net", 
    "https://news.google.com/topstories?hl=ko",
    "https://www.yonhapnews.co.kr",
    "https://news.joins.com"
]

def fetch_news_data(url):
    """뉴스 데이터 수집 시뮬레이션"""
    try:
        # 실제로는 requests.get(url) 사용
        time.sleep(1)  # 네트워크 지연 시뮬레이션
        return f"{url}에서 뉴스 데이터 {len(url)}건 수집 완료"
    except Exception as e:
        return f"{url} 수집 실패: {str(e)}"

# CPU 집약적 작업: 한국어 텍스트 분석
def analyze_korean_text(text_data):
    """한국어 텍스트 분석 (CPU 집약적)"""
    # 복잡한 분석 작업 시뮬레이션
    word_count = 0
    for _ in range(1000000):
        word_count += len(text_data) % 100
    
    return f"텍스트 '{text_data[:20]}...' 분석 완료: {word_count}"

korean_texts = [
    "파이썬은 훌륭한 프로그래밍 언어입니다",
    "한국에서 파이썬 개발자가 늘어나고 있습니다", 
    "데이터 분석과 인공지능 분야에서 파이썬이 인기입니다",
    "웹 개발에서도 파이썬을 많이 사용합니다"
]

# 새 프로세스가 이 파일을 다시 import할 때 아래가 또 실행되지 않도록 막는다
if __name__ == "__main__":
    # 스레드풀로 동시 수집
    print("뉴스 데이터 수집 시작...")
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(fetch_news_data, url) for url in korean_news_sites]

        for future in futures:
            result = future.result()
            print(result)

    end_time = time.time()
    print(f"총 소요시간: {end_time - start_time:.2f}초")

    # 프로세스풀로 CPU 집약적 작업 병렬 처리
    print("\n한국어 텍스트 분석 시작...")
    start_time = time.time()

    with ProcessPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(analyze_korean_text, text) for text in korean_texts]

        for future in futures:
            result = future.result()
            print(result)

    end_time = time.time()
    print(f"총 소요시간: {end_time - start_time:.2f}초")
