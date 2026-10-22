# [2권 Chapter 17. 분산·대규모 학습: 메모리를 아끼고 GPU를 늘리기 · 17.13 실습: 옷 분류기를 세 가지 방법으로 학습하기 · manuscript-vol2/chapters/17-distributed-training.md:1318]
"""b13 실습의 한 걸음을 '데이터 기다림'과 'GPU 계산·통신'으로 나눠 잰다."""
import time

import torch
import torch.distributed as dist
from torch import nn
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader
from torch.utils.data.distributed import DistributedSampler

from b13_실습 import 옷_데이터, 옷CNN, 전체_배치, 준비      # 실습의 부품을 그대로 쓴다

에폭_수 = 5


def main() -> None:
    장치, 분산 = 준비()
    rank = dist.get_rank() if 분산 else 0
    전체 = dist.get_world_size() if 분산 else 1
    if rank == 0:
        옷_데이터(True)
    if 분산:
        dist.barrier()
    학습셋 = 옷_데이터(True)
    GPU당 = 전체_배치 // 전체
    샘플러 = DistributedSampler(학습셋, shuffle=True, seed=0) if 분산 else None
    로더 = DataLoader(학습셋, batch_size=GPU당, sampler=샘플러, shuffle=샘플러 is None)
    torch.manual_seed(0)
    모델 = 옷CNN().to(장치)
    if 분산:
        모델 = DDP(모델)
    옵티마이저 = torch.optim.Adam(모델.parameters(), lr=1e-3)
    손실_함수 = nn.CrossEntropyLoss()
    데이터_시간 = 계산_시간 = 0.0
    걸음 = 0
    시작 = time.perf_counter()
    for 에폭 in range(에폭_수):
        if 샘플러 is not None:
            샘플러.set_epoch(에폭)
        t0 = time.perf_counter()
        for x, y in 로더:
            t1 = time.perf_counter()                  # 여기까지가 배치를 기다린 시간
            x, y = x.to(장치), y.to(장치)
            옵티마이저.zero_grad()
            손실_함수(모델(x), y).backward()
            옵티마이저.step()
            if 장치.type == "cuda":                  # GPU 일이 정말 끝날 때까지 (16장 16.2절)
                torch.cuda.synchronize()
            elif 장치.type == "mps":
                torch.mps.synchronize()
            t2 = time.perf_counter()                  # 여기까지가 계산과 통신 시간
            데이터_시간 += t1 - t0
            계산_시간 += t2 - t1
            걸음 += 1
            t0 = time.perf_counter()
    전체_시간 = time.perf_counter() - 시작
    if rank == 0:
        print(f"[GPU {전체}개 × {GPU당}장] 걸음 {걸음}번, 전체 {전체_시간:.1f}초 = "
              f"데이터 기다림 {데이터_시간:.1f}초 + GPU 계산·통신 {계산_시간:.1f}초 "
              f"(걸음당 데이터 {데이터_시간 / 걸음 * 1000:.1f}ms, 계산 {계산_시간 / 걸음 * 1000:.1f}ms)")
    if 분산:
        dist.destroy_process_group()


if __name__ == "__main__":
    main()
