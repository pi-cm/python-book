#!/bin/zsh
# 블록 하나 또는 여러 개를 fill.py와 같은 조건으로 실행한다
D=${0:a:h}
cd /Users/changmin/git/python-book
for f in "$@"; do
  echo "===== $f"
  BOOK_DATA_DIR=$D/../data uv run -q --no-project --with torch --with numpy --with scikit-learn --with pandas python -W ignore $D/$f
done
