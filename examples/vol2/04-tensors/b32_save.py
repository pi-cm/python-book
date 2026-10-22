# [2권 Chapter 4. 텐서: 숫자를 담는 그릇 · 4.9 텐서 저장하고 불러오기 · manuscript-vol2/chapters/04-tensors.md:1136]
import tempfile
from pathlib import Path

import torch

기온 = torch.tensor([[ 2.0, 13.5, 25.7, 15.0],
                     [ 4.5, 15.0, 25.0, 17.5],
                     [ 1.0, 14.0, 26.0, 15.5]])

with tempfile.TemporaryDirectory() as 폴더:      # 연습용 임시 폴더 (끝나면 지워진다)
    경로 = Path(폴더) / "기온.pt"
    torch.save(기온, 경로)
    다시 = torch.load(경로)
    print(다시.shape, torch.equal(기온, 다시))

    # 여러 개는 딕셔너리로 묶어 한 파일에
    torch.save({"기온": 기온, "도시": ["가람시", "나래시", "다솜시"], "단위": "°C"},
               Path(폴더) / "묶음.pt")
    묶음 = torch.load(Path(폴더) / "묶음.pt")
    print(묶음["도시"], 묶음["기온"][0])

    # 주의: 슬라이스를 저장하면 원본 메모리 전체가 같이 저장된다
    큰_텐서 = torch.zeros(1_000_000)
    torch.save(큰_텐서[:10], Path(폴더) / "조각.pt")
    torch.save(큰_텐서[:10].clone(), Path(폴더) / "복사.pt")
    for 이름 in ["조각.pt", "복사.pt"]:
        print(이름, f"{(Path(폴더) / 이름).stat().st_size:,}바이트")
