import torch

# 두 도시의 (기온, 습도)를 화살표로 본다
서울 = torch.tensor([3.0, 4.0])
부산 = torch.tensor([6.0, 8.0])

길이 = (서울 ** 2).sum().sqrt()            # 피타고라스: 제곱해서 더하고 제곱근
print("서울 화살표의 길이:", 길이.item(), torch.linalg.norm(서울).item())
print("두 점 사이 거리   :", torch.linalg.norm(부산 - 서울).item())
print("두 배로 늘리기    :", (서울 * 2).tolist())
