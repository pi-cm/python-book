#!/bin/bash
# 블록 하나를 fill.py와 같은 환경으로 실행
D=/private/tmp/claude-501/-Users-changmin-git-python-book/e14a96f2-1a68-4a7a-918b-2027747e5566/scratchpad/v2c20
cd $D/run
for b in "$@"; do
echo "=== $b"
HF_HOME=$D/../hf HF_HUB_OFFLINE=1 TRANSFORMERS_VERBOSITY=error HF_HUB_DISABLE_PROGRESS_BARS=1 TOKENIZERS_PARALLELISM=false \
uv run -q --no-project --python 3.12 --with torch --with numpy --with torchvision --with "fastapi[standard]" --with pillow --with pytest --with onnxruntime --with onnx --with onnxscript --with transformers python -W ignore $D/$b.py
done
