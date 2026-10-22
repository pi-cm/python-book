import onnx

from 배포도구 import ONNX로_내보내기, 불러오기, 옷CNN

모델 = 불러오기(옷CNN, "fashion_cnn.pt")
ONNX로_내보내기(모델, "fashion_cnn.onnx")
그래프 = onnx.load("fashion_cnn.onnx").graph

print("[계산 순서]")
for 노드 in 그래프.node:
    print(f"  {노드.op_type:8} {', '.join(노드.input)} → {', '.join(노드.output)}")

print("[저장된 숫자]")
개수 = 0
for 값 in 그래프.initializer:
    배열 = onnx.numpy_helper.to_array(값)
    개수 += 배열.size
    print(f"  {값.name:22} {str(배열.shape):16} {배열.dtype}")
print(f"합계 {개수:,}개 / PyTorch 파라미터 {sum(p.numel() for p in 모델.parameters()):,}개")
