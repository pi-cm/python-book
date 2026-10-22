uv run python b13_실습.py          # 1) GPU 하나, 256장씩
uv run python b13_실습.py --누적 4  # 2) GPU 하나, 64장씩 4번 누적
uv run torchrun --nproc_per_node=2 --master_addr=127.0.0.1 --master_port=29500 b13_실습.py   # 3) GPU 2개 × 128장
