# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.5 모양 바꾸기 · manuscript-vol2/chapters/04-tensors.md:670]
import torch

행렬 = torch.arange(6).reshape(2, 3)
print(행렬)
print("보폭(stride):", 행렬.stride())       # 다음 행으로 3칸, 다음 열로 1칸

전치 = 행렬.T
print(전치)
print("보폭(stride):", 전치.stride())       # 같은 메모리를 다른 보폭으로 읽는다
print("같은 메모리?", 전치.data_ptr() == 행렬.data_ptr())
print("이어져 있나?", 전치.is_contiguous())

정리본 = 전치.contiguous()                  # 보이는 순서대로 새로 늘어놓은 복사본
print("보폭(stride):", 정리본.stride(), "이어져 있나?", 정리본.is_contiguous())
print("같은 메모리?", 정리본.data_ptr() == 행렬.data_ptr())
print(정리본.view(6))                       # 이제 view도 된다
