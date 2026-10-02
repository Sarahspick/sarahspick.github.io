# Shorts Factory: 기업의 비밀 쇼츠 자동 제작

대본 JSON 하나를 넣으면 1080x1920 쇼츠 MP4가 나옵니다.

- **클래식 레이아웃**: 같은 영상을 흐리게 깐 배경 + 가운데 1:1 영상(클립마다 4:3·16:9·최대 9:16) + 상단 고정 제목
- **큰 자막**: 1~3단어씩 나레이션에 정확히 맞춰 톡톡 튀어나옴, 핵심 단어는 노란색
- **자연스러운 AI 목소리**: Microsoft 뉴럴 음성(기본 Brian, +20% 빠르게). 단어 타이밍을 엔진이 직접 제공
- 첫 문장 = 훅(빨간 화살표 + 타격음), 문장·줄마다 하드컷, 펀치 줌, 천천히 밀어 들어가는 줌
- **인터넷에서 받은 실제 효과음**을 단어 타이밍에 배치 (직접 합성한 소리 없음, 전환 바람소리 없음)
- 배경음악은 넣지 않음 (업로드할 때 유튜브에서 직접 추가)
- 인용 카드(보도·성명·뉴스) + CLASSIFIED / DROPPED 도장
- 업로드용 제목, 설명, 해시태그, 출처·푸티지 크레딧 자동 작성 (`*_upload.txt`)
- 음량 -14 LUFS (유튜브 기준)

레퍼런스 채널 분석: [docs/reference_analysis.md](docs/reference_analysis.md)

## 빠른 시작

### Windows 노트북 (결과가 바로 다운로드 폴더로)

1. 이 `shorts-factory` 폴더를 노트북에 받기
2. `tools\windows_setup.bat` 더블클릭 (Python, ffmpeg, 패키지, 폰트·효과음 설치, 1회)
3. `tools\windows_render.bat` 더블클릭하면 `C:\Users\hw487\Downloads`에 저장

### 리눅스 / 클라우드 세션

```bash
pip install -r requirements.txt num2words
python tools/fetch_assets.py
python make_short.py scripts/*.json                                   # output/ 에 저장
python make_short.py scripts/x.json --voice en-US-AndrewMultilingualNeural --rate +25%
```

## 파일 구조

```
make_short.py            렌더링 CLI
channel.json             기본 목소리·속도·발음 사전
scripts/*.json           영상 1개 = 대본 1개 (영어/한국어 각각)
factory/gfx.py           흐린 배경, 제목, 자막 조각, 화살표·커서·도장, 인용 카드
factory/voice.py         edge 뉴럴 음성(단어 타이밍) / Kokoro 오프라인 대체
factory/media.py         yt-dlp 다운로드(yt:/bili:), 크롭, 프레임 리더
factory/sfx.py           효과음 음량 정규화
factory/render.py        타임라인, 자막 조각, 오디오 믹스, 인코딩
tools/fetch_assets.py    폰트·아이콘·효과음 다운로드 (models 옵션: 오프라인 음성)
tools/find_footage.py    각 장면용 원본 영상 후보 검색 (유튜브 / 빌리빌리)
tools/bili_search.py     빌리빌리 빠른 검색 (제목·길이·조회수)
tools/dm_search.py       데일리모션 검색
tools/grab.py            원본 영상 병렬 다운로드 (bili:/yt:/dm:)
tools/sheet.py           원본 영상 컨택트 시트 (구간 고르기용)
tools/qa.py              렌더 결과 점검 (싱크 일치율, 효과음 위치, 2fps 시트)
tools/cutcheck.py        컷 경계 검사: 클립 시작·끝에 앞뒤 장면이 스치면 시작 초를 자동 보정
tools/voice_samples.py   목소리 샘플 영상 (영어·한국어 목소리 전부를 번호 붙여 한 영상에)
assets/sfx_library.json  효과음 목록 + 원본 URL + 라이선스
```

## 대본 형식

```jsonc
{
  "id": "mercedes_bounce", "lang": "en",
  "title": "Mercedes' secret *sand escape* mode 🤯",   // 상단 고정 제목, *강조*
  "aspect": "1:1",                                      // 기본 영상 비율
  "pronounce": {"GLE": "G L E"},                        // 자막은 그대로, 읽기만 다르게
  "hook": {
    "lines": ["This SUV can bounce", "itself out of sand."],
    "clip": "c_spray",
    "annotate": [{"type": "arrow", "at": 0, "x": 0.5, "y": 0.52, "angle": 30}],
    "sfx": [{"id": "boom", "at": "word:bounce"}]
  },
  "sentences": [
    {"lines": ["It's stuck in a dune.", "Wheels spinning."], "clips": ["c_side", "c_front"]},
    {"lines": ["…and the whole car starts *rocking*."], "clip": "c_rock", "punch": true,
     "pause_after": 1.1, "sfx": [{"id": "boom", "at": "word:rocking"}, {"id": "omg", "at": "end+0.05"}]}
  ],
  "clips": {
    "c_rock": {"src": "bili:BV1m4411P7Fs", "start": 182.2, "focus": [0.6, 0.5]},
    "c_side": {"src": "yt:VIDEO_ID", "start": 12.5, "aspect": "4:3", "src_zoom": 1.2},
    "card_x": {"kind": "card", "tag": "news", "outlet": "Motor1", "date": "2021", "headline": "..."}
  }
}
```

- 시간 기준(`at`): `start`, `end`, `line2`, `word:단어`, 숫자(초), `+0.1`/`-0.2` 오프셋
- 문장 옵션: `clip` 또는 줄마다 `clips`, `punch`(펀치 줌), `pause_after`(초), `sfx`, `annotate`
- 주석(`annotate`): `arrow`, `circle`, `cursor`(클릭 소리 자동), `stamp`(도장 소리 자동)
- 클립 옵션
  - `src`: `yt:ID`, `bili:BV...`, URL, 로컬 파일
  - `start`: 시작 초 / `aspect`: `1:1`, `4:5`, `4:3`, `16:9`, `9:16`
  - `focus`: 크롭 중심 `[x, y]` 또는 `auto` / `src_zoom`: 원본 확대(자막·워터마크 잘라내기)
  - `speed`: 슬로모션 등 / `kb`: 줌 시작·끝
- `src`를 받을 수 없으면 노란 라벨의 자리표시 화면으로 대신 렌더링

## 효과음 (전부 인터넷에서 받은 실제 파일)

| id | 소리 | 출처 |
|---|---|---|
| `boom` | Vine boom | SB4K 밈 사운드보드 (GitHub) |
| `ding` | 정답 띠링 | SB4K |
| `omg` / `wow` / `wow_amazing` | Oh my god / Wow incredible | SB4K |
| `gasp` / `ooh` | 관중 헉 / 오오오 | SB4K |
| `get_out` / `wait_what` / `how_possible` / `no_way` | GET OUT! / Wait, what? 등 | SB4K |
| `dun_dun` | 둔둔둔 (반전) | SB4K |
| `mouse_click` / `switch` / `stamp` | 마우스 클릭 / 버튼 / 도장 쾅 | pingthings office 팩 (CC0) |
| `click` / `confirm` / `correct` | UI 클릭 / 확인음 / "Correct!" | Kenney (CC0) |

밈 효과음(SB4K)은 라이선스 파일이 없는 밈 모음입니다. `sfx_library.json`의 `license` 칸으로 구분해 둡니다.

## 목소리

기본: `edge` 엔진 `en-US-BrianMultilingualNeural`, 속도 `+20%`. 대본의 `"voice"` 또는 `--voice`, `--rate`로 교체합니다.

| 구분 | 목소리 (`tools/voice_samples.py`에 전체 ID) |
|---|---|
| 영어, 미국 남성 | Brian (기본), Andrew, Christopher, Guy, Eric, Roger, Steffan |
| 영어, 미국 여성 | Ava, Emma, Aria, Jenny, Michelle |
| 영어, 영국·호주·캐나다 | Ryan, Thomas, Sonia, Libby / William, Natasha / Liam, Clara |
| 한국어 원어민 | `ko-KR-HyunsuMultilingualNeural`(현수), `ko-KR-InJoonNeural`(인준), `ko-KR-SunHiNeural`(선희) |
| 한국어 다국어 | 이름에 `Multilingual`이 붙은 목소리는 한국어 대본도 읽습니다 (Brian, Andrew, Ava, Emma 등). 영어판과 같은 목소리로 한국어판을 만들 수 있습니다 |

- 인터넷 없이 쓰려면 `"voice": {"engine": "kokoro", "name": "am_michael"}` + `python tools/fetch_assets.py models`
- **ElevenLabs** (유료): 환경 변수 `ELEVENLABS_API_KEY`에 키를 넣고, `channel.json`이나 대본의 `"voice"`를 `{"engine": "elevenlabs", "voice_id": "<목소리 ID>", "model": "eleven_v4", "settings": {"speed": 1.1}, "format": "mp3_44100_192"}` 형식으로 바꿉니다. 응답은 `work/elevenlabs_cache/`에 저장돼 같은 문장을 다시 렌더링해도 크레딧이 들지 않습니다. 후보 비교는 `python tools/voice_samples.py`(ElevenLabs 후보, `--engine edge`는 무료 목소리)로 합니다. `format`의 192kbps는 Creator 요금제 이상에서만 되고, 기본값은 128kbps입니다. 글자 단위 타이밍을 받아 자막 싱크가 지금과 같이 맞습니다. 키는 저장소나 채팅에 절대 넣지 않습니다.
- **Typecast** (유료): 환경 변수 `TYPECAST_API_KEY`에 키를 넣고 `{"engine": "typecast", "voice_id": "tc_...", "model": "ssfm-v30", "tempo": 1.1, "emotion": "normal", "intensity": 1.0}` 형식으로 지정합니다. 단어 타이밍을 API에서 받아 자막 싱크가 맞고, 응답은 `work/typecast_cache/`에 저장됩니다.
- 언어별 기본 목소리: `channel.json`의 `"voices": {"ko": {...}}`가 그 언어 대본의 기본 목소리가 됩니다. 없으면 `"voice"`를 씁니다. 대본의 `"voice"`가 가장 우선합니다.
- 다른 유료 음성은 `factory/voice.py`에 `_synth()`만 구현한 클래스를 추가하면 됩니다. 단어 타이밍이 없으면 음성인식으로 자동 정렬합니다.

### 목소리 고르기

- **샘플 영상**: `python tools/voice_samples.py`는 같은 문장을 목소리마다 실제 쇼츠 화면에 입혀 영상 한 편으로 만듭니다. 영어 20개와 한국어 14개이고, 화면에 번호와 이름이 나옵니다. 결과는 `output/<날짜>_voice_samples_EN_KO.mp4`와 번호표 `.txt`입니다. 옵션으로 `--lang ko`, `--only Brian SunHi`, `--rate +10%`를 쓸 수 있습니다. 앱 업로드 한도(30MB)에 맞게 기본 28MB로 인코딩하고, 크기는 `--max-mb`로 바꿉니다.
- **직접 들어보기**: Microsoft Edge 브라우저에서 아무 페이지나 열고 `Ctrl+Shift+U`(소리 내어 읽기)를 누른 뒤, 음성 옵션에서 `Microsoft BrianMultilingual Online (Natural)` 같은 목소리를 고르면 됩니다. 이 엔진과 같은 목소리이고, 속도도 거기서 바꿔 볼 수 있습니다. 한국어는 한국어 페이지에서 `SunHi`, `InJoon`, `HyunsuMultilingual`을 고르세요.

## 원본 영상(푸티지) 고르기

```bash
python tools/bili_search.py "Amazon Kiva robots" "亚马逊 仓库 机器人"   # 후보 찾기
python tools/grab.py bili:BV1P44y1r7DB bili:BV12G411t7Dp            # 받기 (work/sources/)
python tools/sheet.py bili:BV1P44y1r7DB 12 72 1.5                    # 12초부터 72초 동안 1.5초 간격 시트
python make_short.py scripts/amazon_robots.en.json
python tools/cutcheck.py --fix amazon_robots                          # 컷 경계 자동 보정 (1초 이내 이동만)
python make_short.py scripts/amazon_robots.en.json                   # 보정 후 다시 렌더
python tools/qa.py amazon_robots                                     # 결과 점검
```

- 고른 영상의 ID와 시작 초를 `clips`의 `src`, `start`에 넣으면 됩니다
- 브랜드 공식 영상(공식 광고·프레스 영상)을 우선 사용합니다
- 원본에 박힌 자막·워터마크는 `src_zoom`과 `focus`로 잘라냅니다 (예: `"src_zoom": 1.2, "focus": [0.5, 0.42]`)
- 클라우드 서버에서는 유튜브가 봇 확인을 요구해 다운로드가 막힙니다. 그래서 같은 영상이 올라간 빌리빌리를 씁니다. 노트북에서는 유튜브(`yt:`)도 정상 동작합니다.
- 데일리모션(`dm:`)은 로그인 없이 받으면 288p라서 화질이 부족합니다.

## 수익화 체크리스트

- YPP 조건: 구독자 1,000명 + (최근 90일 쇼츠 조회수 1,000만 또는 최근 12개월 시청시간 4,000시간)
- "재사용 콘텐츠" 심사 대비: 원본을 그대로 이어 붙이지 말고, 설명 나레이션·자막·인용 카드·편집으로 새 가치를 더하기
- 출처와 푸티지 크레딧을 설명란에 표기 (`*_upload.txt`에 자동 생성)
- 가능하면 공식 프레스 영상 사용 (Content ID 위험 감소)
