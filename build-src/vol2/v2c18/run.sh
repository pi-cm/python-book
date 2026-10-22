#!/bin/sh
# 블록 하나를 fill.py와 같은 환경으로 실행
D=$(dirname "$0"); cd "$D/run" || exit 1
MLFLOW_DISABLE_AGENT_HINT=1 uv run -q --no-project --python 3.12 --with torch --with numpy --with torchvision --with scikit-learn --with tensorboard --with mlflow --with optuna --with pyyaml python -W ignore ../$1.py
