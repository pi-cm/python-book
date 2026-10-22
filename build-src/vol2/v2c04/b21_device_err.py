import torch

if torch.backends.mps.is_available():
    gpu = torch.ones(3, device="mps")
    cpu = torch.ones(3)
    try:
        gpu + cpu
    except RuntimeError as e:
        print("오류:", str(e)[:120])
    print(gpu + cpu.to("mps"))
