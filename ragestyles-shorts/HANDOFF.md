# RageStyles 쇼츠 인수인계 문서 (2026-09-29)

새 Claude 세션(다른 계정 포함)이 이 문서 하나만 읽고 바로 이어서 일할 수 있게 쓴 문서입니다.
저장소 루트의 `HANDOFF.md`는 다른 프로젝트(Sarah's Pick) 문서이니 건드리지 않습니다.
문서 안의 규칙이 서로 부딪히면 "3. 채널 오너 취향"의 최신 항목이 우선입니다.

## 0. 새 세션 시작 순서

1. GitHub 연결: 새 계정에서 https://claude.ai/connect-github 로 Sarahspick GitHub 계정을 연결하고, 저장소 `Sarahspick/sarahspick.github.io`에 Claude GitHub App이 설치돼 있는지 확인합니다.
2. 새 세션을 만들 때 저장소 `Sarahspick/sarahspick.github.io`를 선택합니다.
3. 네트워크: 세션 제목 표시줄의 클라우드 환경 메뉴 → Edit → Network access 를 넓힙니다. Full 이 제일 간단하고, 허용 목록 방식이면 아래 도메인을 넣습니다.
   `archive.org`, `*.archive.org`, `images-api.nasa.gov`, `images-assets.nasa.gov`, `commons.wikimedia.org`, `upload.wikimedia.org`, `assets.mixkit.co`, `huggingface.co`, `*.hf.co`, `cdn.jsdelivr.net`, `raw.githubusercontent.com`, `i.ytimg.com`, `www.youtube.com`, `pypi.org`, `files.pythonhosted.org`, `download.pytorch.org`
4. 첫 메시지로 아래를 붙여넣습니다.

```
RageStyles 유튜브 쇼츠 작업을 이어서 해줘.
1) git fetch origin claude/exciting-wright-b23t6c 후 그 브랜치를 기준으로 작업해 (이 세션에 지정된 브랜치가 따로 있으면 그 브랜치를 이 커밋에서 시작해서 거기로 push).
2) ragestyles-shorts/HANDOFF.md 를 끝까지 읽고 규칙과 취향을 그대로 따라.
3) bash ragestyles-shorts/setup.sh 로 소스 영상과 효과음을 받아 (Demucs, whisper 까지 필요하면 --full).
4) 준비되면 다음 영상 아이디어 3개를 먼저 제안해줘.
```

5. 참고 영상(사용자가 예전에 채팅에 올린 40M 조회수 쇼츠 5개)은 저작권 때문에 커밋하지 않았습니다. 분석이 다시 필요하면 채팅에 다시 올려야 합니다. 분석 결과는 `BENCHMARK.md`에 있습니다.

## 1. 프로젝트 요약

* 채널: RageStyles (https://www.youtube.com/@Rage_Styles), 프로필 사진은 헤드폰 낀 슈퍼사이언 손오공 (노랑, 주황, 빨강 그라데이션과 흰 스티커 테두리).
* 시청자: 영어권 전 세계, 20~40대 성인.
* 주제: 운동, 헬스, 스포츠, 경쟁, 동기부여.
* 결과물: 1080x1920, 30fps, H.264 + AAC, 약 10~35초, 라우드니스 -14 LUFS.
* 음악: 영상에는 넣지 않습니다. 사용자가 업로드할 때 유튜브에서 직접 넣습니다. 채널에 원래 쓰던 헬스 음악은 절대 쓰지 않습니다.

## 2. 절대 규칙

* 소스는 합법적인 것만: 퍼블릭 도메인, NASA, CC BY / CC BY-SA (설명란 크레딧 필수), 원작자 허락, 유료 라이선스. 무단 재업로드, 텍스트만 덮는 편집, 다운로드 툴 우회는 하지 않습니다.
* 유튜브 영상은 이 환경에서 재생과 다운로드가 봇 확인으로 막혀 있습니다. 우회하지 않습니다. 분석은 정지 프레임(`i.ytimg.com/vi/<id>/hq1.jpg` 등)과 사용자가 채팅에 올린 파일로만 합니다.
* 네트워크 정책을 우회하지 않습니다. 403 으로 막힌 호스트는 사용자에게 알리고 허용 목록 추가를 부탁합니다.
* 구글 드라이브에 개인 민감 문서(여권, 신분증, 통장 사본, 계약서)가 있습니다. 절대 열거나 사용하지 않습니다.
* 유튜브 쿠키, 비밀번호, 계정 정보를 요구하거나 다루지 않습니다.
* 저장소가 공개(public)입니다. 원본 영상(`work/`), Mixkit 효과음 파일(`assets/sfx_mixkit/*.mp3, *.wav`), 사용자가 올린 참고 영상은 커밋하지 않습니다. 완성된 쇼츠 mp4 와 UPLOAD_INFO.md 는 `Downloads/` 에 커밋합니다.
* 대시 기호("—", "-")는 영상 문구, 설명, 채팅 답변에서 쓰지 않습니다. 쉼표와 마침표로 씁니다.
* 커밋 메시지와 산출물에 모델 이름을 쓰지 않습니다. 커밋 서명 줄은 그 세션의 안내를 따릅니다.
* PR 은 사용자가 요청할 때만 만듭니다.

## 3. 채널 오너 취향 (시간순으로 쌓인 피드백, 아래쪽이 최신)

콘텐츠
* 실제 1:1 대결, 스토리가 있는 콘텐츠. 서로 관련 없는 영상 두 개를 이어 붙이는 것은 안 됩니다.
* 유명인(예: 우사인 볼트)과 시청자가 많은 나라(미국, 러시아, 유럽, 아시아) 중심. "자메이카 vs 남아공" 같은 건 아무도 관심 없습니다.
* 1900년대 옛날 영상은 좋습니다. 사람들이 처음 보는 영상이라서요.
* NASA 운동 영상은 매우 좋습니다 (c2 극찬). 하지만 NASA 사람들이 노는 영상(아폴로 "having fun")은 방향이 아닙니다.
* 군대 영상(미군 DVIDS)은 채널 방향이 아닙니다.
* 가끔 팩트체크를 합니다 (예: 샌도우 영상은 에디슨 본인이 아니라 에디슨 스튜디오가 촬영).

편집
* 첫 프레임에 제목과 자막이 이미 보여야 합니다 (첫 프레임이 썸네일이 되는 경우 대비). 렌더러가 t=0 자막은 페이드 없이 바로 그립니다.
* 2~4초마다 컷. 지루한 구간이 없어야 합니다 ("도파민"). 한 테이크뿐이면 줌과 프레이밍을 바꿔 컷을 만듭니다 (c4 v2 참고).
* 원본 소리가 우선이고 끝까지 이어져야 합니다. c7 v1 은 14.5초 이후가 무음이라 지적받았습니다. `qa.py` 가 1.5초 이상 무음을 경고합니다. 무성 영화는 예외 (업로드 때 음악).
* 효과음은 최소한. 직접 합성한 효과음(라이저, 제트기 소리)은 이상하다는 평가. 전환 휘시 정도는 괜찮고, 쓸 때는 Mixkit 같은 실제 음원을 씁니다.
* 흔들림, 글리치, 과한 효과 금지. 프로필 배지 금지 (사람들이 클릭 안 함).
* 배경: 같은 영상을 크게 늘려 블러 처리하고 어둡게 한 것이 최고. 검정이나 흰색 단색 배경은 싫어합니다. 원본이 어두운 영상은 `darken` 을 0.8~0.95 로 올립니다.
* 영상 비율: 1:1 (또는 조금 더 세로). 4:3 은 영상이 작아 보여서 안 됩니다. 2:3 처럼 긴 비율은 자막 자리가 유튜브 UI 에 가려지므로 `box_w` 를 줄여서 씁니다 (예: 4:5 는 `"box_aspect": 0.8, "box_w": 880`).
* 제목은 위쪽(영상 박스 바로 위) 위치가 좋다고 했습니다. 자막은 영상 바로 아래.
* 폰트는 Dela Gothic One. 색은 프로필 사진의 슈퍼사이언 색: 흰 글자, 강조는 노랑→주황 그라데이션(`*단어*`), 더 센 강조는 주황→빨강(`~단어~`), 테두리는 진한 갈색.

## 4. 지금까지 만든 영상과 반응

| 파일 | 내용 | 반응 |
|---|---|---|
| Downloads/01, 02 | 로봇팔 운동, 스페셜올림픽 데드리프트 (초기 스타일, TTS 내레이션) | 재미 없음, 편집 방식 별로 |
| Downloads/new4 b1~b4 | 미군 DVIDS 영상 | 군대는 방향 아님, 합성 효과음 과함, 서로 관련 없는 영상 짜깁기 |
| new5 c1 | 1951 체력 테스트 10종 (진행 바, 반전 자막) | 1900년대 영상 좋다는 평 |
| new5 c2 | NASA 우주 레그데이 (내레이션에서 Demucs 로 음악 제거, 단어 단위 자막) | 매우매우 훌륭함, 다만 첫 프레임에 텍스트 필요 |
| new5 c3 | 200m 남아공 vs 자메이카 | 매우 지루함 |
| new5 c4, new6 c4 | 최초의 보디빌더 샌도우 1894 | 그럭저럭 좋음, 검정 배경이 싫음 |
| new6 c5 | 잭 존슨 vs 제프리스 1910 | 따로 언급 없음 |
| new6 c6 | 아폴로 16 달에서 놀기 | 방향 아님 |
| new6 c7 | 1949 대학 아크로바틱 (원본 내레이션) | 원본 소리 좋음, 그런데 뒤에 소리가 빠짐 |
| new7 c4 v2, c7 v2 | 새 스타일 적용본 (블러 배경, 1:1, 새 폰트, 자막 영상 아래, c7 은 끝까지 원본 소리) | 사용자 확인 전 |

## 5. 파이프라인

설치와 소스 받기
```
bash ragestyles-shorts/setup.sh           # 렌더 의존성 + core 소스 + Mixkit 효과음 + 스모크 테스트
bash ragestyles-shorts/setup.sh --full    # + torch(cpu), faster-whisper, demucs, Demucs 가중치, NASA 내레이션 분리본
python3 pipeline/fetch_sources.py --list  # 무엇이 받아졌는지
python3 pipeline/fetch_sources.py commons # Wikimedia 클립 (429 제한 때문에 4분 간격으로 천천히)
```
소스 목록과 라이선스, 사용처는 `sources/manifest.json` 에 있습니다. DVIDS 크레딧은 `sources/dvids_sources.json`, 효과음 출처는 `sources/sfx_sources.json`, Mixkit 라이선스 메모는 `assets/sfx_mixkit/LICENSE.md`.

렌더
```
cd ragestyles-shorts
python3 pipeline/bench.py plans6/c7_1949_acrobatics_v2.json                          # work/renders/<id>.mp4
python3 pipeline/bench.py plans6/c7_1949_acrobatics_v2.json --frames 0,150,300 --stills /tmp/st   # 스틸만 빠르게
python3 pipeline/qa.py work/renders/<id>.mp4 sheet.jpg                                  # 컨택트시트, LUFS, 피크, 무음 구간
```
전송은 SendUserFile (30MB 제한). 넘으면 다시 인코딩:
`ffmpeg -i in.mp4 -c:v libx264 -preset slow -crf 21 -maxrate 7M -bufsize 14M -c:a copy -movflags +faststart out.mp4`

플랜 JSON (새 스타일 예시는 `plans6/c7_1949_acrobatics_v2.json`)
* `layout`: 생략하면 기본값 `{"mode": "blur", "box_aspect": 1.0, "box_top": 300}`. 키: `mode` (blur, meme, full), `box_aspect`, `box_top` (px), `box_y` (0~1 중심), `box_w`, `darken` (블러 배경 밝기, 기본 0.5), `bg` (meme 배경색).
* `shots[]`: `src` (`archive/Exercise1949` 처럼 `work/` 아래 경로, 확장자가 mp4 가 아니면 붙여 씀), `in`, `dur`, `speed`, `interp`, `zoom` (숫자 또는 [시작, 끝]), `cx`, `cy`, `ease`, `punch` ([{at, zoom, cx, cy, ramp, until}]), `audio` (원본 소리 사용), `af` (voice, film, ambience 필터), `audio_db`, `grade` ({sat, contrast, sharpen}), `bw`, `fade_in`, `fade_out`, 샷별 `layout`, `box_aspect`, `darken`.
* `captions[]`: `t`, `d`, `text`, `style`, `anim` (기본 pop, 제목은 none). 텍스트 문법: `*노랑 강조*`, `~주황 강조~`, `:flexed-biceps:` 같은 Noto 이모지 이름, `:flag-us:` 국기, `\n` 줄바꿈, `\*` 는 별표 그대로. 위치 덮어쓰기 `x`, `y` (0~1), 대상에 고정은 `shot` + `x`, `y`. 크기와 모양 덮어쓰기: size, color, font, italic, stroke, max_w, max_lines, align, line_gap, bg, pad, upper, shadow.
* 스타일: `title` (영상 위 제목), `cap` (영상 아래 자막), `big` (영상 아래 큰 대문자 라벨), `tag` (주황 알약), 예전 스타일 `sub`, `label`, `chapter`, `meme`, `top`, `action`, `list`, `story`, `big_anton`, `tag_old`, `title_old`.
* `marks[]`: `arrow` (빨간 화살표), `circle` (손그림 빨간 원, `shot` 기준 좌표), `progress` (n 개 중 k, 진행 바), `dim` (화면 어둡게).
* `audio_clips[]`: 다른 샷 위에 원본 소리를 까는 J컷. `{src, in, dur, t, af, db, fade}`.
* `sfx[]`: `{t, name, db}`. `mk:` 로 시작하면 Mixkit (`mk:1143_cinematic_whoosh_deep_impact`), 아니면 `assets/sfx/` 합성음 (오너가 싫어하니 쓰지 않기).
* `lufs`: 목표 라운드니스 (-14).

기타 도구
* 대사 받아쓰기: faster-whisper `small.en` 또는 `medium.en`, `word_timestamps=True` 로 컷 지점을 단어 경계에 맞춥니다 (c7 v1 은 "fitness" 중간에서 잘렸던 것을 v2 에서 고침).
* 음악 제거: Demucs htdemucs (`python3 -m demucs --repo work/models/demucs -n htdemucs --two-stems vocals`). 가중치는 dl.fbaipublicfiles.com 이 막혀 있어 Hugging Face 미러를 씁니다.
* 음악 섞임 검사: panns_inference (선택).
* 소스 찾기: `python3 tools/commons_search.py out.json "strongman" "deadlift"` (Wikimedia Commons 영상, 라이선스 포함), `python3 tools/youtube_cc_search.py "deadlift world record"` (유튜브 CC 라이선스 영상 검색 결과만, 다운로드는 안 됨).
* 받아쓴 대사: `sources/transcripts/` (Exercise1949 전체 대사, 초 단위).
* 브라우저: Playwright 크로미움은 `/opt/pw-browsers` 에 있음. 프록시 인증서를 NSS 에 먼저 등록해야 합니다: `certutil -A -d sql:/root/.pki/nssdb -t "C,," -n ccr-agent-proxy -i /root/.ccr/agent-proxy-ca.crt`.

## 6. 소스별 메모

* Internet Archive (Prelinger, Coronet 교육영화, 에디슨 필름, 1910 복싱): 퍼블릭 도메인. 설명란에 출처 표기.
* NASA (images.nasa.gov): 저작권 없음. 크레딧 NASA, "NASA 가 채널을 보증하지 않음" 문구 권장.
* Wikimedia Commons: CC BY / BY-SA. 저자와 라이선스를 설명란에 반드시 표기. BY-SA 소스를 쓰면 그 영상도 BY-SA 로 표기. `safp_100m` 은 TV 중계 캡처라 권리가 불확실하므로 쓰지 않습니다. upload.wikimedia.org 는 429 제한이 심해서 한 번 시도 후 4~5분 쉬기.
* Mixkit 효과음: 상업적 유튜브 사용 가능, 표기 불필요, 파일 자체 재배포 금지 (그래서 git 에서 뺐습니다. 예전 커밋 기록에는 남아 있습니다).
* DVIDS: 미군 영상, 방향이 아니라 보류. 쓸 경우 "The appearance of U.S. Department of War (DoW) visual information does not imply or constitute DoW endorsement." 문구 필수.
* 막힌 곳: 유튜브 영상 스트림(googlevideo.com), dl.fbaipublicfiles.com, github.com releases, Pexels 와 Pixabay (Cloudflare 확인 페이지).

## 7. 더 재미있는 영상을 구하는 방법 (오너 질문 8 답변 요약)

1. 유명 선수가 나오는 옛 뉴스릴과 스포츠 필름: Universal Newsreel (1929~1967, 유니버설이 미국 국립문서보관소에 기증한 뒤 퍼블릭 도메인으로 알려짐, 소리 있음), 1930년 이전에 공개된 미국 필름(공개 후 95년이 지나 퍼블릭 도메인), 미국 의회도서관의 초기 필름. 조 루이스, 베이브 루스, 잭 뎀프시 같은 유명인이 나옵니다. archive.org 에서 받을 수 있어 이 환경에서 바로 가능. 쓰기 전에 항목마다 권리 표기를 확인하고, 올림픽 경기 장면은 IOC 가 권리를 주장하니 뉴스릴이라도 피합니다.
2. CC BY 스포츠 영상: 유튜브 검색 필터의 Creative Commons (예: dt5nR7_CsbY, 파블로 나코네치니 505kg 데드리프트, CC BY 확인됨). 이 환경은 유튜브 다운로드가 막혀 있으니 같은 영상이 Wikimedia Commons 에 옮겨져 있는지 찾거나("From YouTube" 템플릿), 업로더에게 원본 파일을 받습니다.
3. 원작자 허락: 헬스 인플루언서, 스트롱맨, 지역 대회 채널에 DM 으로 크레딧 조건 사용 허락을 받고, 파일은 사용자가 채팅에 올립니다. 기존 규칙과 가장 잘 맞는 방법.
4. 유료 라이선스: ViralHog, Newsflare, Jukin Media(현 Trusted Media Brands), Storyful 같은 바이럴 영상 라이선스 업체. 가장 재미있는 영상이 많지만 비용이 들고 업체 표기 조건이 붙습니다.
5. 직접 촬영: 헬스장 챌린지, 1:1 대결을 오너가 찍어서 올리기.
6. 무료 스톡(Pexels, Pixabay, Mixkit 영상): 합법이지만 스토리가 약합니다. Pexels 와 Pixabay 는 여기서 막혀 있어 사용자가 받아서 올려야 합니다.
* 하지 말 것: 올림픽, 세계육상, UFC 같은 공식 중계 영상 재사용 (Content ID 와 저작권 경고).

## 8. 다음 아이디어 (방향에 맞는 것)

* 조 루이스 vs 막스 슈멜링 1938 (미국 vs 독일, 1936 패배 후 1라운드 KO 복수극): Universal Newsreel 에서 찾기.
* 잭 뎀프시 vs 제스 윌러드 1919 (1라운드에만 다운 7번, 1919년 공개작이라 미국 퍼블릭 도메인): archive.org 에서 찾기.
* 1904 세인트루이스 올림픽 마라톤의 황당한 실화 (팩트체크 필수, 퍼블릭 도메인 사진이나 필름 필요).
* 1900년대 스트롱맨 (샌도우 후속, 의회도서관 필름).
* NASA 운동 2탄: ARED 스쿼트, 데드리프트 (`nasa_extra` 그룹 소스 이미 목록에 있음).
* 세계 최강의 사나이 아틀라스 스톤 (`wsm_stones`, CC BY 3.0).
* 유도 세계선수권 한판승 (`judo_2011`, CC BY 3.0, 에스토니아 vs 브라질이라 국가 흥미는 약함).
