# [2권 Chapter 17. 분산·대규모 학습: 메모리를 아끼고 GPU를 늘리기 · 17.1 학습 중 GPU 메모리는 어디에 쓰일까 · manuscript-vol2/chapters/17-distributed-training.md:111]
GB = 1024 ** 3
# 파라미터 하나당 바이트 수 (float32로 학습할 때)
내역 = {"파라미터": 4, "기울기": 4, "Adam 1차 모멘트": 4, "Adam 2차 모멘트": 4}
학습_바이트 = sum(내역.values())
print(" + ".join(f"{k} {v}" for k, v in 내역.items()), f"= 파라미터당 {학습_바이트}바이트")

for 이름, 개수 in [("0.5B", 494_032_768), ("1B", 1_000_000_000), ("7B", 7_000_000_000)]:
    print(f"{이름:>4}: 추론(bfloat16) {개수 * 2 / GB:5.1f}GB, "
          f"학습(float32+Adam) {개수 * 학습_바이트 / GB:6.1f}GB, "
          f"학습(float32+SGD) {개수 * 8 / GB:5.1f}GB")
print("활성화는 따로: 배치 크기와 입력 길이에 비례해서 더 든다")
