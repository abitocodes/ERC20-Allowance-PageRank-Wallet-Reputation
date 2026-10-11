# audiobook-ko: 학위 논문 쉬운 한국어 번역본 오디오북

쉬운 한국어 번역본(`../../overleaf-github-ko/`)을 귀로 듣는 오디오북이에요. 대본은 `script/`에, 음성 파일은 `audio/`에 둬요.

- 번역본을 그대로 읽지 않고 듣는 말로 옮겼어요. 그림과 표는 말로 풀었어요. 수식, 인용 번호, 번호로 된 참조, 코드 이름은 뜻으로 바꿨어요.
- 내용은 번역본과 같아요. 주장, 결과, 숫자, 한계, 판정을 바꾸거나 더하거나 빼지 않았어요.
- 대본 기준은 [`SCRIPT-GUIDE.md`](SCRIPT-GUIDE.md)에 있어요.

## 대본

| 파일 | 내용 | 예상 길이 |
|---|---|---|
| `script/00-여는-말.md` | 제목과 지은이, 듣는 방법, 초록, 줄임말과 기호 | 약 10분 |
| `script/01-서론과-연구-문제.md` | 1장 | 약 40분 |
| `script/02-앞선-연구-살펴보기와-이론의-틀.md` | 2장(그림 세 개를 말로 묘사) | 약 66분 |
| `script/03-연구-방법.md` | 3장(그림 세 개, 알고리즘 두 개를 말로) | 약 94분 |
| `script/04-구현과-실증-결과.md` | 4장(결과 표 열일곱 개, 그림 네 개를 말로) | 약 80분 |
| `script/05-논의.md` | 5장 | 약 63분 |
| `script/06-결론과-앞으로-할-일.md` | 6장 | 약 16분 |
| `script/07-참고문헌.md` | 참고문헌 안내(목록은 PDF에서) | 1분 미만 |
| `script/08-부록.md` | 부록 일곱 개 | 약 75분 |

예상 길이는 1초에 6음절로 읽는다고 보고 센 값이에요. 모두 합치면 7시간 남짓이고, 실제 길이는 음성에 따라 달라져요.

## 휴대폰 앱으로 듣기

- `listen/audiobook-ko.epub`: 장마다 나뉘고 차례가 있는 전자책 파일이에요.
- `listen/audiobook-ko.txt`: 같은 내용의 글자 파일이에요.
- 두 파일 모두 숫자를 한글로 풀어 썼어요(예: 오천오백이십일 개, 영 점 삼육). 그래서 어떤 앱의 음성이 읽어도 똑같이 읽혀요.
- 문서를 AI 음성으로 읽어 주는 앱(예: ElevenReader, @Voice Aloud Reader)에서 파일을 가져오기로 열어 들으면 돼요.
- 대본을 고친 뒤에는 `python3 tools/make_listen_files.py`로 두 파일을 다시 만들어요.

## 음성 만들기

```bash
pip install requests imageio-ffmpeg
python3 tools/synthesize.py --backend google              # Google Cloud TTS
python3 tools/synthesize.py --backend google --list-voices
python3 tools/synthesize.py --backend melo                # MeloTTS 한국어
```

- `google`: 환경 변수 `GOOGLE_TTS_API_KEY`의 API 키로 Google Cloud Text-to-Speech를 불러요. 한국어 Chirp3-HD 음성을 먼저 고르고, 없으면 Neural2, WaveNet 순서로 골라요. 요금은 Google 요금표를 따라요.
- `melo`: 공개 모델인 MeloTTS 한국어 음성을 이 컴퓨터의 CPU로 돌려요. 모델 파일을 Hugging Face에서 받아야 해요.
- 제목과 문단을 하나씩 합성해 `.cache/`에 모아 두고, 제목 앞뒤와 문단 사이에 쉼을 넣어 장마다 MP3 하나(64kbps)로 묶어요. 중간에 끊겨도 다시 실행하면 이어서 만들어요.
- 숫자는 `tools/normalize.py`가 한국어 읽기로 바꿔요. 예를 들어 `5,521개`는 오천오백이십일 개, `0.36`은 영 점 삼육, `37번`은 서른일곱 번으로 읽어요.

## 원문이 바뀌었을 때

1. 번역본에서 바뀐 절의 대본을 같은 기준으로 고쳐요.
2. `python3 tools/check_script.py script/<파일> ../../overleaf-github-ko/<번역본 파일>`로 검사해요.
3. `tools/synthesize.py`를 다시 실행해요. 바뀐 문단만 새로 합성해요.
