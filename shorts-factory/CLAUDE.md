# shorts-factory: 작업 규칙과 현재 상태

사용자와는 한국어로 대화합니다. 채널 주제는 기업의 비밀과 "와" 소리 나는 기술입니다. 사용법 전체는 README.md에 있습니다.

## 사용자가 정한 규칙

- 효과음은 인터넷에서 받은 실제 파일만 씁니다 (`assets/sfx_library.json`). 직접 합성하지 않습니다.
- 배경음악은 넣지 않습니다. 업로드할 때 사용자가 넣습니다.
- 전환 효과음(whoosh)은 넣지 않습니다. 장면은 하드컷으로만 넘깁니다.
- AI로 만든 영상은 쓰지 않습니다. 실제 영상을 편집하고 설명을 더해 가치를 만듭니다. 출처와 크레딧은 `_upload.txt`에 적습니다.
- 화면에 채널명·프로필·인증 마크를 넣지 않습니다. 흐린 같은 영상을 배경으로 깔고, 1:1(최대 9:16) 영상, 상단 고정 제목, 1~3단어 자막을 씁니다.
- 첫 3초 훅과 반전이 있는 이야기로 구성합니다.
- 목표는 영어판과 한국어판 한 세트입니다. 한국어판은 아직 만들지 않았습니다.
- 기존 영어 쇼츠 12편(`scripts/*.en.json`)은 확정본이라 그대로 업로드합니다. 다시 만들거나 고치지 않습니다.

## 목소리 (2026-09-29 기준)

- 무료 Edge 목소리를 샘플 영상(`tools/voice_samples.py`)으로 들려줬습니다. 영어는 Andrew(따뜻하고 자신감 있는 남성)가 가장 낫다는 평가였지만, 전체적으로 로봇 같다고 했습니다. 한국어(원어민·다국어 모두)는 "못 들어줄 수준"이었습니다.
- 그래서 ElevenLabs로 바꿔 완전 자동화합니다.
  - 키는 환경 변수 `ELEVENLABS_API_KEY`로만 받습니다. 채팅으로는 받지 않습니다.
  - 엔진은 `factory/voice.py`의 `ElevenLabsNarrator`입니다. `/with-timestamps` 글자 타이밍을 단어 타이밍으로 바꿉니다. 모의 응답으로만 테스트했고, 실제 호출 검증이 필요합니다.
- 2026-09-29 확인 결과 (키 연결됨)
  - 사용자는 Creator라고 했지만 API(`GET /v1/user/subscription`)로는 **Starter**(월 4만 자, 목소리 슬롯 10개)로 나옵니다. `mp3_44100_192`를 요청하면 403이 납니다. Creator로 확인되기 전까지 `format`은 기본값 128kbps로 둡니다.
  - Eleven v4(`eleven_v4`)는 한국어와 `/with-timestamps`를 지원하고, `voice_settings.speed`도 받습니다. v4 Turbo는 크레딧이 절반입니다.
  - 라이브러리 목소리는 My Voices에 추가하지 않아도 voice_id로 바로 쓸 수 있습니다 (슬롯을 쓰지 않음).
  - `ElevenLabsNarrator`는 성공한 응답을 `work/elevenlabs_cache/`에 저장합니다. 같은 문장·목소리·설정을 다시 렌더링하면 크레딧이 들지 않습니다.
  - `tools/voice_samples.py`의 기본 엔진이 ElevenLabs입니다 (`--engine edge`로 예전 목록). 후보는 `ELEVEN_VOICES`에 있습니다 (영어 9명, 한국어 원어민 9명). 샘플 영상 `output/20260929_voice_samples_elevenlabs_EN_KO.mp4`를 보냈고, 사용자의 선택을 기다립니다.
- 사용자가 고르면 `channel.json` 기본 목소리를 `{"engine": "elevenlabs", "voice_id": ..., "model": "eleven_v4", "settings": {"speed": 1.1}}`로 바꾸고, 한국어판은 대본의 `"voice"`로 한국어 목소리를 지정합니다.
- 크레딧을 아낍니다. 샘플 문장은 짧게 하고, 같은 문장을 불필요하게 다시 생성하지 않습니다.

## 새 세션에서 처음 할 일

모든 작업은 브랜치 `claude/upbeat-ramanujan-72d6wv`에 있습니다. main 브랜치에는 없습니다. 먼저 그 브랜치를 가져와 자기 작업 브랜치로 이어받습니다.

새 컨테이너에는 git에 없는 것들이 빠져 있어서, 먼저 준비합니다.

```bash
apt-get install -y --no-install-recommends ffmpeg      # 기본 이미지에 없음 (이모지 폰트는 있음)
pip install -r requirements.txt num2words
python tools/fetch_assets.py                            # 폰트·아이콘·효과음
python tools/grab.py bili:BV1m4411P7Fs                  # 목소리 샘플 영상에 쓰는 벤츠 원본
```

- 키 확인: `ELEVENLABS_API_KEY`가 비어 있으면, 사용자에게 환경 설정에 넣고 새 세션을 열어 달라고 안내합니다. 채팅으로 받지 않습니다.
- 요금제 확인: `GET /v1/user/subscription`의 `tier`가 creator 이상이면 음성 설정에 `"format": "mp3_44100_192"`를 넣습니다.

## 작업 팁

- 클라우드에서는 유튜브 다운로드가 봇 확인에 막힙니다. 빌리빌리 재업로드(`bili:`)를 씁니다.
- `pkill -f`를 쓰면 자기 셸까지 죽습니다. `ps`로 PID를 찾아 kill합니다.
- `pip install num2words`가 docopt 빌드에서 실패하면 `pip install docopt-ng && pip install --no-deps num2words`로 설치합니다.
- 결과물은 앱으로 보냅니다 (업로드 한도 30MB). 사용자 노트북 저장 위치는 `C:\Users\hw487\Downloads`입니다.
