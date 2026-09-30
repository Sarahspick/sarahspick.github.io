# shorts-factory: 작업 규칙과 현재 상태

사용자와는 한국어로 대화합니다. 채널은 언어별로 둘입니다 (2026-09-29 확정, `channel.json`의 `"channels"`):

| 언어 | 채널명 | 유튜브 핸들 | 메인 테마 색 (강조색) |
|---|---|---|---|
| 영어 | Top Techs | @toptechs-1 | 일렉트릭 블루 #168BFF (22, 139, 255) |
| 한국어 | 기발한 회사들 | @기발한회사들 | 레드 #F5333F (245, 51, 63) |

강조색(제목·자막의 *강조* 단어)은 대본의 `lang`에 맞는 채널 색으로 자동 적용됩니다 (`gfx.set_accent`). 채널 주제는 기업의 비밀과 "와" 소리 나는 기술입니다. 사용법 전체는 README.md에 있습니다.

## 사용자가 정한 규칙

- **2026-09-30 피드백 (이전 7편은 못 쓰는 수준이라고 함, 소스 재사용 금지)**
  - 중국 냄새 금지: 중국 회사·중국 영상·중국어 글자가 보이는 소재는 피합니다. 삼성, 아마존, 애플처럼 누구나 아는 회사 위주.
  - **How 궁금증 전략**: "폴드 화면은 어떻게 접힐까?", "아마존은 이걸 어떻게 했을까?"처럼 원리를 궁금하게 만들고 풀어줍니다.
  - **훅의 반전은 첫 문장 안에** (3초 안). 뜸 들이지 않습니다.
  - **Vine Boom 금지** (`sfx_allow`에서 뺌). 효과음은 whoosh, click2, sparkle, dingding, question 정도로 가볍게.
  - 한국어 목소리 1.2배 빠르게 (Typecast tempo 1.32).
  - **자막은 모든 영상에서 화면 정중앙** (`gfx.CAPTION_CY = H // 2`).
  - 원본에 자막이 박혀 있으면 흐림 대신 클립 `"cover": [[x0,y0,x1,y1]]`(원본 비율): 그 자리를 검정 박스로 완전히 덮고 우리 자막을 그 박스 위에 정확히 얹습니다 (Ken Burns 끄기 `"kb": [1, 1]`). 흐림만 한 자막은 거슬린다고 함.
  - 빨간 동그라미·화살표는 렌더 후 프레임을 보고 정확히 대상 위에 있는지 확인합니다.
  - 아마존 드론 편 평가: "매우 훌륭, 깔끔, 아주 잘했다" → 이 구성(How 훅, 실사 + 근접 촬영, 반전, 한마디 마무리)이 기준.
  - **인트로 효과음 (모든 영상, 2026-09-30):** 영상 시작 0초에 드라이브 '17. 물음표'(`question`)가 울립니다 (`channel.json`의 `"intro_sfx"`). 대신 쿵 하는 sub hit를 원하면 `"intro_sfx": "boom2"`(13. BOOM). 대본마다 `"intro_sfx"`로 바꿀 수도 있어요.
  - **마지막 줄은 질문 금지.** 감상평, 재밌는 한마디, 비유로 끝냅니다 (예: "주름이 흉터였다면, 이제는 잔주름 수준.", "피자보다 빠르고, 웬만한 사람보다 눈치가 빨라요."). 댓글 유도는 고정 댓글에서 드립으로.

- **중국어가 들리면 절대 안 됩니다 (2026-09-30).** 원본 사운드는 `factory/speech.py`(SenseVoice)가 클립마다 말소리를 검사해서, 말(어느 언어든)이 있으면 그 구간 원본 소리를 자동으로 끕니다 (경고 `orig audio muted`). 말소리를 꼭 살려야 하는 클립만 `"orig_speech": true`.
- **영상 소스는 최신 고화질 영어권 소스** (2026-09-30): 중국 사이트(빌리빌리)와 Pexels 같은 저화질 스톡은 쓰지 않습니다. 순서: 유튜브(`yt:`) → 틱톡(`tt:<영상 id>`, 1080x1920) → X(`x:<status id>`, 1080p). 영상을 만든 뒤 사용자가 보고 허락한 것만 업로드합니다.
  - 유튜브: `YT_COOKIES_B64`(base64 쿠키 파일)를 `work/yt_cookies.txt`로 풀고, Node 22(`/opt/node22/bin/node`)로 JS 챌린지를 풉니다 (`media.ytdlp_opts`). 그래도 이 서버 IP는 자주 429/403/봇 확인에 막힙니다(2026-09-30 대부분 실패). 막히면 틱톡·X로.
  - 틱톡은 `pip install "yt-dlp[default,curl-cffi]"`가 필요하고, 1080p는 h265라 `format_sort res:1080`으로 고릅니다.
  - 틱톡 영상 id는 웹 검색(`allowed_domains: tiktok.com`)으로 찾습니다. 틱톡 검색 페이지는 JS라 못 읽습니다.
- 효과음: 사용자 구글 드라이브 `자주쓰는 효과음` 22개가 `assets/sfx/user/`에 있습니다 (id: boom2, punch, whoosh, click2, riser1, riser8, question, dingding, tada, huh, sparkle, cartoon_pop 등, `sfx_library.json`). 드라이브 폴더는 링크 공유라 `python tools/fetch_assets.py sfx`가 gdown으로 다시 받습니다.
- 빨간 화살표(`"type": "arrow"`, x/y는 영상 박스 안 비율, angle은 화살표 방향)와 빨간 동그라미(`"type": "circle"`, r 픽셀)를 적극 씁니다.
- 배경음악: Memory Reboot 같은 유행곡은 저작권 음원이라 파일로 넣지 않습니다. 업로드할 때 유튜브 쇼츠 편집기에서 라이선스된 음원으로 넣습니다 (나레이션 -14 LUFS라 음악은 10~15% 정도로).

- 효과음은 인터넷에서 받은 실제 파일만 씁니다 (`assets/sfx_library.json`). 직접 합성하지 않습니다.
- 허용 효과음 (2026-09-29): 타격음 계열(Vine Boom, Sub, Hit)과 마우스 클릭(딸깍), 가벼운 whoosh만. wow·incredible·빰빰빰(dun_dun)·omg·군중 반응 같은 거슬리는 소리는 전부 금지. `channel.json`의 `"sfx_allow"`에 없는 효과음은 렌더링에서 자동으로 빠지고 경고가 남습니다. 지금 라이브러리에 있는 허용 소리는 boom, mouse_click, click뿐이고 sub, hit, whoosh 파일은 아직 없습니다 (넣으려면 실제 파일을 찾아 `sfx_library.json`에 추가).
- 배경음악은 넣지 않습니다. 업로드할 때 사용자가 넣습니다.
- 장면은 하드컷으로 넘깁니다. 전환 whoosh는 가벼운 것만 허용 (2026-09-29부터).
- AI로 만든 영상은 쓰지 않습니다. 실제 영상을 편집하고 설명을 더해 가치를 만듭니다. 출처와 크레딧은 `_upload.txt`에 적습니다.
- 화면에 채널명·프로필·인증 마크를 넣지 않습니다. 상단 고정 제목, 1~3단어 자막을 씁니다.
- **화면 비율은 영상마다 판단 (중요, 2026-09-29).** 선호: 9:16 전체 화면 > 3:4 > 1:1. 원본이 세로이거나 사진처럼 세로로 잘라도 주인공이 다 보이면 9:16 전체 화면(`"aspect": "9:16"`, 흐린 배경 없음). 가로 원본에서 9:16으로 자르면 핵심 장면(차 전체 등)이 잘리면 3:4, 그것도 잘리면 1:1. 예: 렉서스 꽈배기 = 9:16 (세로 폰 영상 + 공식 사진 팬), 모래 탈출 SUV = 3:4 (가로 원본, 정면 흔들림 장면의 차가 3:4에 딱 들어감).
- **원본 사운드를 웬만하면 넣습니다** (사용자: 알게 모르게 도움이 많이 됨). 대본의 `"orig_audio": {"lufs": -30}`이면 화면 컷과 똑같이 잘린 원본 소리가 나레이션 밑에 깔립니다 (소스마다 음량 정규화, 클립별 `orig_gain` dB, `null`이면 음소거). 원본에 말소리가 많으면 -32 정도로 낮춥니다.
- 원본에 박힌 외국어 자막·워터마크는 **글자 상자만 정확히** 흐립니다 (사용자: 넓게 흐리면 더 이상함). 자막은 `python tools/textboxes.py <src> --band 0.3 0.85 --centered --json`으로 자막마다 상자와 시작·끝 시간을 자동으로 찾아 클립 `"blur_boxes"`에 넣습니다 (그 시간에만 그 상자만, 가장자리는 부드럽게). 워터마크처럼 계속 있는 것은 딱 맞는 `"blur": [[x0,y0,x1,y1]]`. **한국어판은 가운데 자막을 흐리지 않습니다** (사용자: 흐리면 더 이상해 보임, 워터마크만). 출처는 설명란에 그대로 적습니다.
- **한국어 대본은 영어를 번역하지 않고 `docs/ko_script_guide.md`에 따라 따로 씁니다** (사용자: 번역투가 어색함). 영어 대본은 하던 대로.
- 컷 경계가 문장보다 짧으면 `python tools/cutcheck.py --fix --slow scripts/<대본>.json`: 시작점은 그대로 두고 클립 속도만 낮춰 컷 직전에 끝나게 합니다 (최소 0.5배). 그다음 다시 렌더.
- 사진도 소스로 씁니다 (공식 보도 사진 등): `{"kind": "image", "src": 경로, "url": 원본 URL, "src_zoom": 1.5, "pan": [[fx,fy],[fx,fy]]}`로 사진 위를 천천히 이동하는 샷이 됩니다. 사진 파일은 git에 넣지 않고 `url`에서 다시 받습니다.
- 첫 3초 훅과 반전이 있는 이야기로 구성합니다.
- 목표는 영어판과 한국어판 한 세트입니다. 두 판은 번역본이 아니라 조금씩 다르게 만듭니다 (한국 시청자에 맞춘 표현·단위·훅). 순서: 대본을 언어별로 쓰고 → TTS → TTS 길이에 맞춰 컷을 잘라 이어붙이기. 렌더러가 문장·줄마다 TTS 길이로 클립 길이를 정하므로 두 판의 컷은 자동으로 달라집니다.
- 결과물 전달: 영상마다 `<이름>_text.txt`(제목 / 설명 / 태그 / 댓글을 `___` 줄로 나눈 복붙용 파일, 대본 `upload.comment`가 고정 댓글)를 같이 만듭니다. 사용자 구글 드라이브의 `Claude Youtube Project` 폴더(https://drive.google.com/drive/folders/15ZuFnwkci3M4oeBMUKKiSUU5VHzC-RkW) 안 `Top Techs`(영어), `기발한 기업들`(한국어) 폴더에 넣어 달라고 했습니다. 2026-09-29 세션에는 구글 드라이브 커넥터가 없어서 앱으로만 보냈습니다 (커넥터 연결: claude.ai/customize/connectors, 새 세션부터 적용).
- 두 번째 세트 (2026-09-29): 렉서스 × 미스치프 꽈배기 차 `scripts/lexus_twisted.*.json` (9:16, 빌리빌리 BV1Crh26SEoC 뉴욕 전시 폰 영상 + 렉서스 보도 사진 3장), 모래 탈출 벤츠 GLS `scripts/sand_escape.*.json` (3:4, BV1m4411P7Fs). 유튜브 원본은 이 환경에서 봇 확인에 막혀 못 받습니다 (검색은 됨).
- 세 번째 묶음 (2026-09-29, "재밌게, 최신 영상으로" 5편, 전부 3:4): `robot_fails`(로봇 수난 모음: 6월 사무실 쿵후 로봇 CCTV, 산호세 식당 로봇 폭주, 러시아 AIdol 데뷔 무대 추락, 베이징 하프마라톤. BV1j7KN6ZEG1, 어린이 다친 장면 18.7~37.9초는 쓰지 않음), `xpeng_iron`(9월 8일 IRON 생산 라인 자율 보행 BV1zSbV67ECF + 다리 절개 BV1Ca2uBLELs), `vw_efficiency`(9월 14일 폭스바겐 미션 이피션시 Cd 0.158, 1,278km 충전 1회, BV191es67EiW), `iphone_duo`(9월 9일 발표, 1,999달러, 공식 영상 BV1AyYb6rE1S + 주름 테스트 BV1vtY96bEuZ), `hoverair_versa`(8월 18일, 230g, BV12yaP66EFd). 9월 7일 사오싱 로봇 발차기 사건은 빌리빌리에 영상이 없어서 못 씀.
- 주제 찾기 순서: 웹 검색(최근 1~2달 뉴스) → `tools/bili_search.py`로 실제 영상 확인(중국어 키워드가 잘 걸림) → 받을 수 있는 것만 주제로 확정. 영상 속 날짜(CCTV 타임스탬프 등)와 뉴스 날짜가 다르면 대본에서 날짜를 말하지 않습니다.
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
