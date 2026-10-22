#!/bin/bash
# 블록 하나 실행: run.sh b01_x
D=$(dirname "$0")
for n in "$@"; do echo "=== $n"; (cd $D/work && uv run -q --no-project --with torch --with numpy --with torchvision --with pillow --with pandas python -W ignore $D/$n.py); done
