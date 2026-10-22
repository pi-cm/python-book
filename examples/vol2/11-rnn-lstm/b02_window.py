# [2권 Chapter 11. RNN과 LSTM: 순서가 있는 데이터 · 11.1 순서 데이터의 모양 · manuscript-vol2/chapters/11-rnn-lstm.md:77]
import torch

# 예제용으로 만든 열흘치 하루 평균 기온(°C)
기온 = torch.tensor([3.0, 4.5, 6.0, 5.5, 7.0, 8.5, 8.0, 9.5, 11.0, 10.5])

# 창 크기 3: 사흘을 보고 다음 날을 맞히는 문제로 바꾼다
창 = 3
조각들 = 기온.unfold(0, 창, 1)        # 길이 3짜리 창을 한 칸씩 밀며 잘라 낸다
print(조각들.shape)
print(조각들[:3])

X = 조각들[:-1]                        # 마지막 창은 다음 날 정답이 없으니 뺀다
y = 기온[창:]                          # 각 창의 바로 다음 날
for i in range(3):
    print(X[i].tolist(), "→", y[i].item())

# 순환 신경망이 받는 모양: (배치, 길이, 특성)
X = X.unsqueeze(-1)                    # 하루에 숫자 1개(기온)이니 특성 1
print("입력:", tuple(X.shape), "정답:", tuple(y.shape))
print("같은 메모리를 쓰나?", 조각들.data_ptr() == 기온.data_ptr())
