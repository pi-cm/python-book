#!/bin/bash
# 블록 하나를 fill.py와 같은 환경에서 실행한다
S=/private/tmp/claude-501/-Users-changmin-git-python-book/e14a96f2-1a68-4a7a-918b-2027747e5566/scratchpad
cd $S && HF_HOME=$S/hf HF_HUB_DISABLE_PROGRESS_BARS=1 TRANSFORMERS_VERBOSITY=error TOKENIZERS_PARALLELISM=false uv run -q --no-project --python 3.12 --with torch --with numpy --with transformers --with tokenizers --with datasets --with kiwipiepy --with scikit-learn python -W ignore "$@"
