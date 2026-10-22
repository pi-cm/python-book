import onnx
import onnxruntime as ort
import torch

from 옷도구 import 옷CNN, 시험_데이터

모델 = 옷CNN()
모델.load_state_dict(torch.load("fashion_cnn.pt", weights_only=True))
모델.eval()

묶음 = torch.export.Dim("batch")                  # 이름 붙인 "자유로운 차원"
torch.onnx.export(모델, (torch.zeros(1, 1, 28, 28),), "fashion_cnn_batch.onnx",
                  verbose=False, external_data=False,
                  input_names=["사진"], output_names=["점수"],
                  dynamic_shapes={"x": {0: 묶음}})       # forward(x)의 0번 차원은 자유

모형 = onnx.load("fashion_cnn_batch.onnx")
for 값 in [*모형.graph.input, *모형.graph.output]:
    print(값.name, [d.dim_value or d.dim_param for d in 값.type.tensor_type.shape.dim])

세션 = ort.InferenceSession("fashion_cnn_batch.onnx", providers=["CPUExecutionProvider"])
X, y = 시험_데이터()
for 장수 in [1, 7, 64]:
    print(f"{장수:>5}장 →", 세션.run(None, {"사진": X[:장수].numpy()})[0].shape)
점수 = 세션.run(["점수"], {"사진": X.numpy()})[0]           # 1만 장을 한 번에
print(f"1만 장 한 번에: {점수.shape}, 정확도 {(점수.argmax(axis=1) == y.numpy()).mean():.2%}")
