# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.8 장치: CPU와 GPU 사이 옮기기 · manuscript-vol2/chapters/04-tensors.md:1071]
import torch

if torch.backends.mps.is_available():
    gpu = torch.ones(3, device="mps")
    cpu = torch.ones(3)
    try:
        gpu + cpu
    except RuntimeError as e:
        print("오류:", str(e)[:120])
    print(gpu + cpu.to("mps"))
