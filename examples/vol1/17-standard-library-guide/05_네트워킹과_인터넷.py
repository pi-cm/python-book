"""1권 Chapter 17: 표준 라이브러리 핵심 가이드 — 네트워킹과 인터넷

원고: manuscript/chapters/17-standard-library-guide.md (477줄부터)
"""

# ---- 원고 477줄 ----
import datetime
import json
import urllib.parse
import urllib.request

# 한글 검색어를 포함한 URL 생성
base_url = "https://api.example.com/search"
params = {
    "q": "파이썬 프로그래밍",
    "lang": "ko",
    "limit": 10
}

# URL 인코딩
encoded_params = urllib.parse.urlencode(params)
full_url = f"{base_url}?{encoded_params}"
print(f"요청 URL: {full_url}")

# 한국 공공데이터 API 호출 예제 (모의)
def get_korean_weather(city="서울"):
    """한국 날씨 정보 조회"""
    try:
        # 실제로는 API 키가 필요
        api_url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": f"{city},KR",
            "appid": "YOUR_API_KEY",
            "lang": "kr",
            "units": "metric"
        }
        
        encoded_params = urllib.parse.urlencode(params)
        url = f"{api_url}?{encoded_params}"
        
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                return {
                    "도시": data.get("name", city),
                    "온도": data["main"]["temp"],
                    "날씨": data["weather"][0]["description"]
                }
    except Exception as e:
        print(f"API 호출 오류: {e}")
        return None

# HTTP 서버 만들기
from http.server import HTTPServer, BaseHTTPRequestHandler

class KoreanHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html = """
        <html>
        <head><title>한국어 웹서버</title></head>
        <body>
            <h1>안녕하세요! 파이썬 웹서버입니다</h1>
            <p>현재 시간: {}</p>
        </body>
        </html>
        """.format(datetime.datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분'))
        
        self.wfile.write(html.encode('utf-8'))

# 서버 실행 예제 (주석 처리)
# server = HTTPServer(('localhost', 8000), KoreanHandler)
# print("서버 시작: http://localhost:8000")
# server.serve_forever()
