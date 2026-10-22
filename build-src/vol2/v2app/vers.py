from importlib.metadata import version, PackageNotFoundError
import sys
print(sys.version)
for p in ["torch","torchvision","numpy","scikit-learn","pandas","scipy","matplotlib","statsmodels","pillow","transformers","datasets","tokenizers","huggingface_hub","kiwipiepy","peft","accelerate","tensorboard","mlflow","optuna","pyyaml","onnx","onnxscript","onnxruntime","torchao","fastapi","pydantic","uvicorn","python-multipart","httpx","pytest","joblib"]:
    try: print(p, version(p))
    except PackageNotFoundError: print(p, "-")
