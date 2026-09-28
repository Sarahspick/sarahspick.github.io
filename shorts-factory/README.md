# Shorts Factory: 기업의 비밀 쇼츠 자동 제작

대본 JSON 하나를 넣으면 1080x1920 쇼츠 MP4가 나옵니다.

- AI 나레이션 (Kokoro, 오프라인·무료·상업 이용 가능 Apache-2.0)
- 음성인식으로 맞춘 **문장·단어 단위 싱크 자막** (핵심 단어 노란색 강조)
- **X(트위터) 게시물 스타일 틀**: 원형 프로필, 채널명, 파란 인증 배지, @핸들, 제목
- 첫 2~3초 **훅 화면** (어둡게 + 초대형 2줄 제목 + 빨간 화살표), 첫 프레임이 곧 썸네일
- 16:9 원본을 **4:3 / 1:1로 자동 크롭** (움직임·디테일이 많은 쪽을 따라감)
- 문장 시작마다 하드컷, 펀치 줌, 천천히 밀어 들어가는 줌
- **인터넷에서 받은 실제 효과음**을 단어 타이밍에 맞춰 배치 (직접 합성한 소리 없음)
- 배경음악은 넣지 않음 (업로드할 때 유튜브에서 직접 추가)
- 업로드용 제목, 설명, 해시태그, 출처 목록 (`*_upload.txt`)

레퍼런스 채널 분석: [docs/reference_analysis.md](docs/reference_analysis.md)

## 빠른 시작

### Windows 노트북 (결과가 바로 다운로드 폴더로)

1. 이 `shorts-factory` 폴더를 노트북에 받기
2. `tools\windows_setup.bat` 더블클릭 (Python, ffmpeg, 패키지, 모델·폰트·효과음 설치, 1회)
3. 프로필 사진을 `assets\branding\avatar.png`로 저장 (없으면 임시 아이콘)
4. `tools\windows_render.bat` 더블클릭하면 `C:\Users\hw487\Downloads`에 저장

### 리눅스 / 클라우드 세션

```bash
pip install -r requirements.txt num2words
python tools/fetch_assets.py
python make_short.py scripts/*.json                  # output/ 에 저장
python make_short.py scripts/x.json --theme light     # 라이트 모드
python make_short.py scripts/x.json --voice af_heart  # 다른 목소리
```

## 파일 구조

```
make_short.py            렌더링 CLI
channel.json             채널명, 핸들, 프로필 사진, 테마, 목소리, 발음 사전
scripts/*.json           영상 1개 = 대본 1개 (영어/한국어 각각)
factory/gfx.py           X 게시물 틀, 자막, 훅, 화살표·커서·도장, 인용 카드
factory/voice.py         Kokoro TTS + SenseVoice 정렬 (줄·단어 타이밍)
factory/media.py         yt-dlp 다운로드, 스마트 크롭, 프레임 리더
factory/sfx.py           효과음 음량 정규화
factory/render.py        타임라인, 오디오 믹스(-14 LUFS), 인코딩
tools/fetch_assets.py    모델·폰트·아이콘·효과음 다운로드
tools/find_footage.py    각 장면에 쓸 유튜브 원본 후보 검색
assets/sfx_library.json  효과음 목록 + 원본 URL + 라이선스
```

## 대본 형식

```jsonc
{
  "id": "mercedes_bounce", "lang": "en",
  "title": "게시물 본문(제목) — 이모지 가능 🤯",
  "pronounce": {"GLE": "G L E"},          // 자막은 그대로, 읽기만 다르게
  "hook": {
    "big": ["This SUV can", "*BOUNCE* out of sand"],   // 훅 대형 제목 2줄, *강조*
    "say": "This SUV can literally bounce itself out of sand.",
    "clip": "c_hook",
    "annotate": [{"type": "arrow", "at": 0, "x": 0.56, "y": 0.62, "angle": 35}],
    "sfx": [{"id": "boom", "at": "word:bounce"}]
  },
  "sentences": [
    {"lines": ["This Mercedes GLE is stuck", "deep in a *sand dune*."], "clip": "c_stuck"},
    {"lines": ["This one just", "presses a *button*…"], "clip": "c_screen",
     "annotate": [{"type": "cursor", "at": "line2", "x": 0.52, "y": 0.58}]},
    {"lines": ["…and the whole car", "starts *bouncing*."], "clip": "c_bounce", "punch": true,
     "pause_after": 1.15, "sfx": [{"id": "boom", "at": "word:bouncing"}, {"id": "omg", "at": "end+0.05"}]}
  ],
  "clips": {
    "c_stuck": {"src": "https://www.youtube.com/watch?v=...", "start": 12.5, "aspect": "4:3", "focus": "auto"},
    "c_card":  {"kind": "card", "tag": "news", "outlet": "Motor1", "date": "2021", "headline": "..."}
  }
}
```

- 자막 한 줄은 **30자 안팎**. 넘치면 자동 축소 후 경고
- 시간 기준(`at`): `start`, `end`, `line2`, `word:단어`, 숫자(초), `+0.1`/`-0.2` 오프셋
- 문장 옵션: `clip` 또는 줄마다 `clips`, `punch`(펀치 줌), `pause_after`, `sfx`, `annotate`
- 주석(`annotate`): `arrow`, `circle`, `cursor`(클릭 소리 자동), `stamp`(도장 소리 자동)
- 클립 옵션: `src`(유튜브 URL / 로컬 파일 / 이미지), `start`, `aspect`(`4:3`, `1:1`, `16:9`), `focus`(`auto` 또는 `[x, y]`), `speed`, `kb`(줌 시작·끝), `src_zoom`
- `src`가 없거나 받을 수 없으면 노란 라벨의 **자리표시 화면**으로 대신 렌더링

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

밈 효과음(SB4K)은 라이선스 파일이 없는 밈 모음입니다. 쇼츠에서 흔히 쓰이지만 공식 라이선스가 있는 건 아니므로 `sfx_library.json`의 `license` 칸으로 구분해 둡니다.

## 목소리

기본값 `am_michael`(깊은 남성), 속도 1.15. `--voice`로 교체: `af_heart`·`af_bella`(여성, 품질 최상), `am_fenrir`, `am_puck`, `bm_george`(영국).
유료 음성(ElevenLabs 등)으로 바꾸려면 `factory/voice.py`의 `Narrator.synth`만 교체하면 됩니다. 자막 정렬은 음성인식으로 하므로 어떤 TTS든 그대로 동작합니다.

## 원본 영상(푸티지) 고르기

```bash
python tools/find_footage.py scripts/mercedes_bounce.en.json
```

공식 채널(브랜드 뉴스룸·프레스 영상)을 우선 표시합니다. 고른 URL과 시작 초를 `clips`의 `src`, `start`에 넣으면 됩니다.

## 수익화 체크리스트

- YPP 조건: 구독자 1,000명 + (최근 90일 쇼츠 조회수 1,000만 또는 최근 12개월 시청시간 4,000시간)
- "재사용 콘텐츠" 심사 대비: 원본을 그대로 이어 붙이지 말고, 설명 나레이션·자막·인용 카드·편집으로 새 가치를 더하기
- 출처를 설명란에 표기 (`*_upload.txt`에 자동 생성)
- 가능하면 공식 프레스 영상, CC 라이선스 영상 사용 (Content ID 위험 감소)
- 처음 7초 안에 욕설 넣지 않기 (광고 제한)
