#!/bin/zsh
# 블록 하나 실행: ./run1.sh b01_x
cd "$(dirname $0)/run" && /usr/bin/time -p uv run -q --no-project --python 3.12 --with torch --with numpy --with torchvision --with matplotlib python -W ignore ../$1.py
