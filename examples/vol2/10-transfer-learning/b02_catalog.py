# [2권 Chapter 10. 전이 학습: 남이 학습한 모델 빌려 쓰기 · 10.1 사전학습 모델 불러오기 · manuscript-vol2/chapters/10-transfer-learning.md:70]
from torchvision import models

이름들 = models.list_models(module=models)     # torchvision의 사진 분류 모델 목록
print(f"사진 분류 모델 {len(이름들)}종:", 이름들[:4], "...")

for 이름 in ["mobilenet_v3_small", "resnet18", "efficientnet_b0", "resnet50", "vit_b_16"]:
    w = models.get_model_weights(이름).DEFAULT   # 가중치 정보만 읽는다. 내려받지 않는다
    정확도 = w.meta["_metrics"]["ImageNet-1K"]["acc@1"]
    print(f"{이름:19} 파라미터 {w.meta['num_params'] / 1e6:5.1f}백만, "
          f"파일 {w.meta['_file_size']:6.1f}MB, top-1 {정확도:.1f}%")
