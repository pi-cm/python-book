#!/bin/zsh
# 블록 하나 실행 (fill.py와 같은 조건)
D=/private/tmp/claude-501/-Users-changmin-git-python-book/e14a96f2-1a68-4a7a-918b-2027747e5566/scratchpad/v2c08
cd /Users/changmin/git/python-book/manuscript-vol2/assets/images/ch08
for f in "$@"; do echo "### $f"; uv run -q --no-project --python 3.12 --with torch --with numpy --with scikit-learn --with matplotlib --with torchvision python -W ignore $D/$f.py; done
