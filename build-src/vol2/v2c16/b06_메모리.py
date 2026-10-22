import torch

MB = 1024 ** 2


def 보기(때: str) -> None:
    """지금 할당된 메모리와, PyTorch가 GPU에서 맡아 둔(예약한) 메모리를 보여 준다."""
    print(f"할당 {torch.cuda.memory_allocated() / MB:6.1f} MB | "
          f"예약 {torch.cuda.memory_reserved() / MB:6.1f} MB  ← {때}")


보기("처음")
x = torch.zeros(256, 1024, 1024, device="cuda")      # 2억 6천만 칸 × 4바이트 = 1GB
보기("1GB 텐서를 만든 뒤")
y = x + 1
보기("계산 결과까지")
del x, y
보기("del 한 뒤")
z = torch.zeros(128, 1024, 1024, device="cuda")      # 0.5GB: 맡아 둔 자리를 다시 쓴다
보기("0.5GB를 다시 만든 뒤")
del z
torch.cuda.empty_cache()                              # 맡아 둔 자리를 GPU에 돌려준다
보기("empty_cache 뒤")
print(f"지금까지의 최고 할당: {torch.cuda.max_memory_allocated() / MB:.1f} MB")
