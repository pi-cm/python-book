# [2권 Chapter 16. GPU와 성능: 같은 모델을 더 빠르게, 더 가볍게 · 들어가며: 같은 요리, 다른 주방 · manuscript-vol2/chapters/16-gpu-performance.md:22]
import torch

print("PyTorch    :", torch.__version__)
print("CUDA 빌드  :", torch.version.cuda)
print("GPU 개수   :", torch.cuda.device_count())
속성 = torch.cuda.get_device_properties(0)
print("GPU 이름   :", 속성.name)
print(f"GPU 메모리 : {속성.total_memory / 1024**3:.1f} GB")
print("SM 개수    :", 속성.multi_processor_count)
print("계산 능력  :", f"{속성.major}.{속성.minor}")
print("bfloat16   :", torch.cuda.is_bf16_supported())
