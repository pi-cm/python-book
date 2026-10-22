import gzip
import io

import torch
import torch.nn.utils.prune as prune

from 배포도구 import 불러오기, 시험_데이터, 옷CNN

X, y = 시험_데이터()


def 크기들(모델: torch.nn.Module) -> tuple[float, float]:
    """state_dict의 저장 크기와 gzip으로 압축한 크기(KB)."""
    버퍼 = io.BytesIO()
    torch.save(모델.state_dict(), 버퍼)
    return len(버퍼.getvalue()) / 1024, len(gzip.compress(버퍼.getvalue())) / 1024


for 비율 in [0.0, 0.5, 0.8, 0.9]:
    모델 = 불러오기(옷CNN, "fashion_cnn.pt")
    대상 = [(모델.특징[0], "weight"), (모델.특징[3], "weight"),
            (모델.분류[1], "weight"), (모델.분류[3], "weight")]
    if 비율 > 0:
        # 네 층의 가중치를 한데 모아 절댓값이 작은 것부터 '비율'만큼 0으로
        prune.global_unstructured(대상, pruning_method=prune.L1Unstructured, amount=비율)
        for 층, 이름 in 대상:
            prune.remove(층, 이름)                  # 가림판을 떼고 0을 가중치에 굳힌다
    영 = sum((층.weight == 0).sum().item() for 층, _ in 대상)
    전체 = sum(층.weight.numel() for 층, _ in 대상)
    with torch.no_grad():
        정확도 = (모델(X).argmax(dim=1) == y).float().mean().item()
    저장, 압축 = 크기들(모델)
    print(f"가지치기 {비율:3.0%}: 0인 가중치 {영 / 전체:5.1%}, 정확도 {정확도:.2%}, "
          f"저장 {저장:,.0f}KB, gzip {압축:,.0f}KB")
