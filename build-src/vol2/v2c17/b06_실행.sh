# 이 컴퓨터(노드 하나)에서 프로세스 2개를 띄운다. GPU가 있으면 프로세스마다 GPU 하나씩
uv run torchrun --nproc_per_node=2 --master_addr=127.0.0.1 --master_port=29500 b06_첫_allreduce.py
