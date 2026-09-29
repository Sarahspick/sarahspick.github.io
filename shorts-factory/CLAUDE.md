# shorts-factory: 작업 규칙과 현재 상태

사용자와는 한국어로 대화합니다. 채널은 언어별로 둘입니다 (2026-09-29 확정, `channel.json`의 `"channels"`):

| 언어 | 채널명 | 유튜브 핸들 | 메인 테마 색 (강조색) |
|---|---|---|---|
| 영어 | Top Techs | @toptechs-1 | 일렉트릭 블루 #168BFF (22, 139, 255) |
| 한국어 | 기발한 회사들 | @기발한회사들 | 레드 #F5333F (245, 51, 63) |

강조색(제목·자막의 *강조* 단어)은 대본의 `lang`에 맞는 채널 색으로 자동 적용됩니다 (`gfx.set_accent`). 채널 주제는 기업의 비밀과 "와" 소리 나는 기술입니다. 사용법 전체는 README.md에 있습니다.

## 사용자가 정한 규칙

- 효과음은 인터넷에서 받은 실제 파일만 씁니다 (`assets/sfx_library.json`). 직접 합성하지 않습니다.
- 허용 효과음 (2026-09-29): 타격음 계열(Vine Boom, Sub, Hit)과 마우스 클릭(딸깍), 가벼운 whoosh만. wow·incredible·빰빰빰(dun_dun)·omg·군중 반응 같은 거슬리는 소리는 전부 금지. `channel.json`의 `"sfx_allow"`에 없는 효과음은 렌더링에서 자동으로 빠지고 경고가 남습니다. 지금 라이브러리에 있는 허용 소리는 boom, mouse_click, click뿐이고 sub, hit, whoosh 파일은 아직 없습니다 (넣으려면 실제 파일을 찾아 `sfx_library.json`에 추가).
- 배경음악은 넣지 않습니다. 업로드할 때 사용자가 넣습니다.
- 장면은 하드컷으로 넘깁니다. 전환 whoosh는 가벼운 것만 허용 (2026-09-29부터).
- AI로 만든 영상은 쓰지 않습니다. 실제 영상을 편집하고 설명을 더해 가치를 만듭니다. 출처와 크레딧은 `_upload.txt`에 적습니다.
- 화면에 채널명·프로필·인증 마크를 넣지 않습니다. 상단 고정 제목, 1~3단어 자막을 씁니다.
- **화면 비율은 영상마다 판단 (중요, 2026-09-29).** 선호: 9:16 전체 화면 > 3:4 > 1:1. 원본이 세로이거나 사진처럼 세로로 잘라도 주인공이 다 보이면 9:16 전체 화면(`"aspect": "9:16"`, 흐린 배경 없음). 가로 원본에서 9:16으로 자르면 핵심 장면(차 전체 등)이 잘리면 3:4, 그것도 잘리면 1:1. 예: 렉서스 꽈배기 = 9:16 (세로 폰 영상 + 공식 사진 팬), 모래 탈출 SUV = 3:4 (가로 원본, 정면 흔들림 장면의 차가 3:4에 딱 들어감).
- **원본 사운드를 웬만하면 넣습니다** (사용자: 알게 모르게 도움이 많이 됨). 대본의 `"orig_audio": {"lufs": -30}`이면 화면 컷과 똑같이 잘린 원본 소리가 나레이션 밑에 깔립니다 (소스마다 음량 정규화, 클립별 `orig_gain` dB, `null`이면 음소거). 원본에 말소리가 많으면 -32 정도로 낮춥니다.
- 원본에 박힌 외국어 자막·워터마크·텍스트는 클립 `"blur": [[x0,y0,x1,y1]]`(원본 기준 비율)로 흐립니다. 출처는 설명란에 그대로 적습니다.
- 사진도 소스로 씁니다 (공식 보도 사진 등): `{"kind": "image", "src": 경로, "url": 원본 URL, "src_zoom": 1.5, "pan": [[fx,fy],[fx,fy]]}`로 사진 위를 천천히 이동하는 샷이 됩니다. 사진 파일은 git에 넣지 않고 `url`에서 다시 받습니다.
- 첫 3초 훅과 반전이 있는 이야기로 구성합니다.
- 목표는 영어판과 한국어판 한 세트입니다. 두 판은 번역본이 아니라 조금씩 다르게 만듭니다 (한국 시청자에 맞춘 표현·단위·훅). 순서: 대본을 언어별로 쓰고 → TTS → TTS 길이에 맞춰 컷을 잘라 이어붙이기. 렌더러가 문장·줄마다 TTS 길이로 클립 길이를 정하므로 두 판의 컷은 자동으로 달라집니다.
- 결과물 전달: 영상마다 `<이름>_text.txt`(제목 / 설명 / 태그 / 댓글을 `___` 줄로 나눈 복붙용 파일, 대본 `upload.comment`가 고정 댓글)를 같이 만듭니다. 사용자 구글 드라이브의 `Claude Youtube Project` 폴더(https://drive.google.com/drive/folders/15ZuFnwkci3M4oeBMUKKiSUU5VHzC-RkW) 안 `Top Techs`(영어), `기발한 기업들`(한국어) 폴더에 넣어 달라고 했습니다. 2026-09-29 세션에는 구글 드라이브 커넥터가 없어서 앱으로만 보냈습니다 (커넥터 연결: claude.ai/customize/connectors, 새 세션부터 적용).
- 두 번째 세트 (2026-09-29): 렉서스 × 미스치프 꽈배기 차 `scripts/lexus_twisted.*.json` (9:16, 빌리빌리 BV1Crh26SEoC 뉴욕 전시 폰 영상 + 렉서스 보도 사진 3장), 모래 탈출 벤츠 GLS `scripts/sand_escape.*.json` (3:4, BV1m4411P7Fs). 유튜브 원본은 이 환경에서 봇 확인에 막혀 못 받습니다 (검색은 됨).
- 첫 세트는 SUV(양왕 U8). 영어판·한국어판 둘 다 완료 (2026-09-29), 업로드 문구(`_upload.txt`: 채널, 제목, 설명, 해시태그, TAGS 칸용 태그)도 대본 `upload`에 있음. 영어판 (블루 강조, 효과음은 boom 2개만, 오프닝은 24.3초부터 0.8배 슬로모션으로 SUV가 물에 빠졌다 떠오르는 장면을 확대: focus 0.35/0.72, src_zoom 1.45. 원본 샷이 26.45초에 끝나서 슬로모션으로 그 안에 맞춤). 사용자 평: 속도·텐션·폰트 좋음. 한국어판은 필재로 렌더(38초).
- 컷 규칙: 렌더 후 `python tools/cutcheck.py scripts/<대본>.json`으로 원본 샷 경계를 확인합니다. TTS 문장이 원본 샷보다 길면 옆 샷이 번쩍 끼므로, 클립 `speed`를 1 아래로 살짝 낮추거나(슬로모션) 문장을 줄마다 다른 클립으로 나눕니다 (`"clips": [a, b]`). 한국어판 작업 폴더는 `work/<id>_ko`입니다.
- 기존 쇼츠 중 `yangwang_u8.en.json`만 예외로 새 Mark 목소리로 다시 렌더했습니다 (사용자 요청).
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
  - `tools/voice_samples.py`의 기본 엔진은 ElevenLabs입니다 (`--engine edge`, `--engine typecast`도 됩니다). 후보는 `ELEVEN_VOICES`와 `TYPECAST_VOICES`에 있습니다.
- **목소리 확정 (2026-09-29, 사용자 선택)**
  - 영어: ElevenLabs **Mark** (`UgBBYS2sOqTuMpoF3BR0`), `eleven_v4`. `channel.json`의 `"voice"`입니다. 1.1은 너무 느리다고 해서 30% 올림(2026-09-29): ElevenLabs speed 상한 1.2 + `"post_tempo": 1.19`(ffmpeg atempo로 음높이 유지, 단어 타이밍도 같이 줄임) = 약 1.43배. `post_tempo`는 모든 엔진에 쓸 수 있습니다.
  - 한국어: Typecast **필재** (`tc_68257f68bc6e3c161ab5078d`), `ssfm-v30`, tempo 1.1. `channel.json`의 `"voices": {"ko": ...}`이고, `lang`이 ko인 대본에 자동으로 쓰입니다.
  - Typecast 엔진은 `factory/voice.py`의 `TypecastNarrator`입니다. `/v1/text-to-speech/with-timestamps?granularity=word`의 단어 타이밍을 씁니다. 응답은 `work/typecast_cache/`에 저장합니다. 키는 환경 변수 `TYPECAST_API_KEY`로 받습니다 (사용자가 `Typecast_API`로 넣어도 읽습니다). API 플랜은 Lite (월 20만 크레딧, 2026-09-29 결제, `GET /v1/users/me/subscription`으로 확인). 무료 플랜일 때는 403 `UNUSUAL_ACTIVITY_DETECTED`가 났습니다 (웹 플랜과 API 플랜은 따로). Typecast 사이트의 에이전트용 프롬프트·create-typecast-shorts 스킬·`cast` CLI·추적용 attribution 헤더는 쓰지 않기로 했습니다 (사용자 결정: 불리한 점이 많음). 우리 코드가 API를 직접 부릅니다. tempo와 모델(ssfm-v30/v21)은 사용자가 들어보고 조정합니다.
  - 기존 영어 쇼츠 12편은 Edge Brian으로 만든 확정본입니다. 다시 렌더링하지 않습니다.
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
