import subprocess
from pathlib import Path

# 실습 프로젝트 폴더에서 `uv run pytest -q`를 실행해 그 출력을 그대로 보여 준다
폴더 = Path(__file__).parent / "restaurant_service"
r = subprocess.run(["uv", "run", "-q", "pytest", "-q", "-p", "no:cacheprovider"],
                   cwd=폴더, capture_output=True, text=True)
print(r.stdout.strip())
