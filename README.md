# 파이썬 완전 백과사전

파이썬을 처음 배우는 사람부터 딥러닝 모델을 서비스로 내보내려는 사람까지, 한국어로 차근차근 읽을 수 있게 쓴 책 시리즈입니다.
본문에 실린 코드와 출력은 모두 실제로 실행해서 얻은 그대로입니다.

| 권 | 내용 | 원고 | 예제 |
|---|---|---|---|
| 1권 | 파이썬 (20장) | [`manuscript/`](manuscript/) | [`examples/vol1/`](examples/vol1/) |
| 2권 | PyTorch 딥러닝 (21장, 부록 A~C) | [`manuscript-vol2/`](manuscript-vol2/) | [`examples/vol2/`](examples/vol2/) |
| 3권 | 로봇 | 집필 중 | |
| 4권 | 에이전트 엔지니어링 | 계획 중 | |

## 읽기

원고는 장마다 마크다운 파일 하나입니다. 깃허브에서 `manuscript/chapters/`나 `manuscript-vol2/chapters/`를 열면 바로 읽을 수 있어요.

## 예제 실행

예제는 책의 코드 블록을 블록 하나당 파일 하나로 뽑아 둔 것입니다. 실행 방법은 각 폴더의 README를 보세요.

- [`examples/vol1/README.md`](examples/vol1/README.md)
- [`examples/vol2/README.md`](examples/vol2/README.md)

[uv](https://docs.astral.sh/uv/)가 필요합니다.

## PDF 만들기

[pandoc](https://pandoc.org/)과 XeLaTeX(TeX Live 또는 MacTeX)가 필요합니다. 본문 글꼴(고운바탕, IBM Plex Sans KR)은 `tools/fonts/`에 들어 있습니다.

```bash
uv run python tools/build.py --pdf --vol 1   # output/에 1권 PDF
uv run python tools/build.py --pdf --vol 2   # output/에 2권 PDF
```

한자와 일부 기호는 macOS 시스템 글꼴(AppleMyungjo, Thonburi, Arial Unicode MS)로 찍습니다. 다른 운영체제에서는 `tools/pdf-header.tex`의 해당 글꼴을 설치된 글꼴로 바꾸세요.

## 폴더 구성

- `manuscript/`, `manuscript-vol2/` — 원고(장, 부록, 그림)
- `examples/` — 원고에서 뽑은 실행용 예제
- `tools/` — PDF 빌드(`build.py`), 예제 추출(`extract_examples.py`), 예제 검사(`check_examples.py`)
- `build-src/` — 2권 원고를 만든 작업 재료. 코드 블록을 실행해 출력을 원고에 채우는 스크립트입니다([`build-src/README.md`](build-src/README.md)).

## 라이선스

- **본문**(원고, 그림, PDF): [CC BY-NC-SA 4.0](LICENSE-text)
  출처를 밝히면 자유롭게 읽고 공유하고 고쳐 쓸 수 있습니다. 영리 목적으로는 쓸 수 없고, 고친 결과물도 같은 라이선스로 공개해야 합니다.
- **코드**(`examples/`, `tools/`, `build-src/`의 코드, 원고 속 코드 블록): [MIT](LICENSE)
  업무용이든 개인용이든 마음대로 복사해 쓰세요.
- **글꼴**: `tools/fonts/`의 글꼴은 각자의 [SIL Open Font License](tools/fonts/)를 따릅니다.
- **데이터**: 예제가 내려받는 데이터셋과 모델은 각 제공처의 라이선스를 따릅니다. 출처와 라이선스는 그 데이터를 처음 쓰는 장에 적어 두었습니다.
