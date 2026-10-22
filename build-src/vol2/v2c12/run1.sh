#!/bin/sh
# 블록 하나를 fill.py와 같은 조건으로 실행
cd /private/tmp/claude-501/-Users-changmin-git-python-book/e14a96f2-1a68-4a7a-918b-2027747e5566/scratchpad && uv run -q --no-project --python 3.12 --with torch --with numpy python -W ignore v2c12/$1.py
