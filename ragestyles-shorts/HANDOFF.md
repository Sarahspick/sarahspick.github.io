# RageStyles 쇼츠 인수인계 문서 (2026-09-30, 4차 갱신)

새 Claude 세션(다른 계정 포함)이 이 문서 하나만 읽고 바로 이어서 일할 수 있게 쓴 문서입니다.
저장소 루트의 `HANDOFF.md`는 다른 프로젝트(Sarah's Pick) 문서이니 건드리지 않습니다.
문서 안의 규칙이 서로 부딪히면 "3. 채널 오너 취향"의 최신 항목이 우선입니다.

## ★ 채널 정체성 (2026-09-30 오너 확정, 다른 모든 방향보다 우선)
RageStyles 는 운동, 헬스, 스포츠의 **최신 소식을 가장 빠르게 알리는 채널**입니다. 지금 뜨는 인물과 사건, 그 인물들이 인스타그램과 유튜브에 막 올린 영상을 편집해서 소식으로 전합니다.
* 최신이 먼저: 며칠 안에 나온 사건과 영상 (기록, 대회 결과, 우승, 이변, 인물의 새 발언). 옛날 영상, 이미 지나간 인물(고긴스, 에디 홀, 범스테드 등 오너 판단으로 "트렌드 지남")은 쓰지 않음. 옛 영상 편집은 기법 연습용이었음.
* 형식: new16 d1(고긴스) 방향. 그 인물 본인 목소리로 이어지는 이야기 + 원문 워드 바이 워드 자막(`wordcap`) + 본인 영상 B롤 + 3:4 블러 레이아웃(제목 155px, 영상 370px) + 시작 1초 페이드 + 핵심 순간 줌 펀치, 밝기, 쿵. 목소리가 없는 경기 영상은 s1 방식(짧은 정보 자막 + 발표 순간 효과).
* 소식 확인: 영상 속 사실은 기사(fitnessvolt.com, generationiron.com, barbend.com, 위키백과)로 교차 확인하고 날짜를 적음. 다르면 오너에게 알림.
* 소스: 원 채널 크레딧 + "All rights go to the owners" (오너 방침, 2-1). 인스타그램은 이 환경에서 접속됨 (2-1), 유튜브는 `tools/yt_batch.sh`.

## ★ 지금 트렌드 (2026-09-30 4차 조사, 다음 세션은 여기서 고르기)
* 오너 (2026-09-30): 올림피아 주제는 이제 그만. 칼리스데닉스, 스포츠, 헬스, 러닝, 마라톤, 운동 모티베이션 등 최신 트렌드면 다 좋음. Tren Twins, Sam Sulek 은 쇼츠로 좋다고 봄. David Goggins, Eddie Hall, Chris Bumstead 의 근황 같은 최신 소식을 그들의 인스타그램, 유튜브 영상으로 편집하는 것도 좋음.
* 오너가 받은 외부 트렌드 조사 (다른 AI, 2026-10-01 기준, 우선순위순): 1 Raul Flores 511kg (만듦, r1), 2 Jesse James West (쇠막대 구부리기 등 챌린지, 9/29), 3 Magnus Midtbo (클라이머, 인플루언서 체력 대결), 4 Anatoly (7/26 "Gym CHALLENGE Went Wrong", 청소부가 당하는 반전), 5 Nick Bare (하이브리드, 웨이트+러닝+HYROX, 9/24), 6 Jeff Nippard (칼로리 순위, 1900년부터 운동 변천), 7 Sam Sulek (만듦, s2). 흐름: 신기록과 실력 반전, 종목 간 대결 (보디빌더 vs 클라이머), 하이브리드 운동 (HYROX 35개국 150만 명), Winter Arc 와 Lock In (10월 시작 연말 변화 시리즈), 90일 자기관리. Clavicular (looksmaxxing) 는 인물 중심으로 쓰지 않기 (유튜브가 관련 채널 삭제).
* 아직 안 쓴 최신 소재: Berlin Marathon 2026-09-27 Tigst Assefa 가 다리 경련 (아킬레스 부상설) 속에 2:11:04 로 우승, 세계기록에 68초 모자람 (공식 BMW BERLIN-MARATHON kF2FgCAfKgY 여자 결승, nA5EohZ2S1g 남자 결승 Guye Adola 2:02:51, Abbott WMM 하이라이트 SZvi5gYI-9A, 받아둠). Agnes Ngetich 2026-09-20 코펜하겐 세계로드러닝선수권 하프 1:05:15 여자 단독 세계기록 (영상 소스 빈약). Danny Grigsby 데드리프트 세계기록 (9/24, 소스는 IG 재업로드 채널뿐). Roy Orrantia Static Monsters 세계기록 (Big Loz 해설 bQ2P9JvepWk). Eddie Hall vs Tommy Fury 는 6월이라 지남.
* 업로드 날짜 확인: 쿠키 없이 `yt-dlp --skip-download --print "%(upload_date)s"` 는 절반쯤 봇 확인에 걸림. `tools/yt_batch.sh` 로 받으면 info.json 에 날짜가 있음. 채널 최신 영상 목록은 쿠키 없이 `yt-dlp --flat-playlist "https://www.youtube.com/@채널/videos"` 로 됨 (업로드 순).

## 0. 새 세션 시작 순서

1. GitHub 연결: 새 계정에서 https://claude.ai/connect-github 로 Sarahspick GitHub 계정을 연결하고, 저장소 `Sarahspick/sarahspick.github.io`에 Claude GitHub App이 설치돼 있는지 확인합니다.
2. 새 세션을 만들 때 저장소 `Sarahspick/sarahspick.github.io`를 선택합니다.
3. 네트워크: 세션 제목 표시줄의 클라우드 환경 메뉴 → Edit → Network access 를 넓힙니다. Full 이 제일 간단하고, 허용 목록 방식이면 아래 도메인을 넣습니다.
   `archive.org`, `*.archive.org`, `images-api.nasa.gov`, `images-assets.nasa.gov`, `commons.wikimedia.org`, `upload.wikimedia.org`, `assets.mixkit.co`, `huggingface.co`, `*.hf.co`, `cdn.jsdelivr.net`, `raw.githubusercontent.com`, `i.ytimg.com`, `www.youtube.com`, `pypi.org`, `files.pythonhosted.org`, `download.pytorch.org`, `api.pexels.com`, `videos.pexels.com`, `pixabay.com`, `cdn.pixabay.com`
4. API 키: 같은 환경 설정의 Environment variables 에 `PEXELS_API_KEY`, `PIXABAY_API_KEY` 를 넣습니다 (이름에 PEXELS, PIXABAY 가 들어가면 됩니다). 키는 채팅에 붙여넣지 않습니다.
5. 첫 메시지로 아래를 붙여넣습니다.

```
RageStyles 유튜브 쇼츠 작업을 이어서 해줘.
1) git fetch origin claude/modest-meitner-bb2p2c 후 그 브랜치를 기준으로 작업해 (이 세션에 지정된 브랜치가 따로 있으면 그 브랜치를 이 커밋에서 시작해서 거기로 push).
2) ragestyles-shorts/HANDOFF.md 를 끝까지 읽고 규칙과 취향을 그대로 따라. 맨 위 "★ 채널 정체성" 과 "★ 지금 트렌드" 가 최우선이고, 3장 오너 취향의 최신 항목(2026-09-30)과 2-3 도 꼭 봐.
3) bash ragestyles-shorts/setup.sh --full 로 환경을 준비하고, 드라이브 "자주쓰는 효과음" 폴더에서 묵직한 효과음 6개를 다시 받아 ow_*.wav 로 변환해 (2-3 에 파일 대응표).
4) 유튜브 쿠키(YT_COOKIES_B64)를 새로 바꿨어. bash ragestyles-shorts/tools/yt_batch.sh 로 다운로드가 되는지 먼저 테스트해 (쿠키 값은 절대 출력하지 마). 안 되면 바로 알려줘.
5) "★ 지금 트렌드" 에서 최근 2주 안의 최신 소식 쇼츠 3개를 골라서 (업로드 날짜, 사실은 기사로 교차 확인) 소스 검색, 다운로드, 편집까지 네가 직접 하고, 결과물만 채팅으로 바로 보내줘 (30MB 넘으면 tools/fit_send.sh). 형식은 new16 고긴스 방향 (본인 목소리 이야기 + 원문 워드 바이 워드 자막 + 3:4 블러, 제목 155px, 영상 370px, 시작 1초 페이드).
```

6. 참고 영상(사용자가 예전에 채팅에 올린 40M 조회수 쇼츠 5개)은 저작권 때문에 커밋하지 않았습니다. 분석이 다시 필요하면 채팅에 다시 올려야 합니다. 분석 결과는 `BENCHMARK.md`에 있습니다.

## 1. 프로젝트 요약

* 채널: RageStyles (https://www.youtube.com/@Rage_Styles), 프로필 사진은 헤드폰 낀 슈퍼사이언 손오공 (노랑, 주황, 빨강 그라데이션과 흰 스티커 테두리).
* 시청자: 영어권 전 세계, 20~40대 성인.
* 주제: 운동, 헬스, 스포츠의 최신 소식 (맨 위 "★ 채널 정체성").
* 결과물: 1080x1920, 30fps, H.264 + AAC, 약 10~35초, 라우드니스 -14 LUFS.
* 음악: 영상에는 넣지 않습니다. 사용자가 업로드할 때 유튜브에서 직접 넣습니다. 채널에 원래 쓰던 헬스 음악은 절대 쓰지 않습니다.

## 2. 절대 규칙

* 소스는 합법적인 것만: 퍼블릭 도메인, NASA, CC BY / CC BY-SA (설명란 크레딧 필수), 원작자 허락, 유료 라이선스. 무단 재업로드, 텍스트만 덮는 편집, 다운로드 툴 우회는 하지 않습니다.
* 유튜브 영상은 이 환경에서 재생과 다운로드가 봇 확인으로 막혀 있습니다. 우회하지 않습니다. 분석은 정지 프레임(`i.ytimg.com/vi/<id>/hq1.jpg` 등)과 사용자가 채팅에 올린 파일로만 합니다.
* 네트워크 정책을 우회하지 않습니다. 403 으로 막힌 호스트는 사용자에게 알리고 허용 목록 추가를 부탁합니다.
* 구글 드라이브에 개인 민감 문서(여권, 신분증, 통장 사본, 계약서)가 있습니다. 절대 열거나 사용하지 않습니다.
* 유튜브 쿠키, 비밀번호, 계정 정보를 요구하거나 다루지 않습니다. 예외는 오너가 2026-09-30 에 허락한 `tools/yt_batch.sh` 와 환경 변수 `YT_COOKIES_B64` 뿐이고, 값은 절대 출력, 커밋, 채팅하지 않습니다 (2-3 참고).
* 저장소가 공개(public)입니다. 원본 영상(`work/`), Mixkit 효과음 파일(`assets/sfx_mixkit/*.mp3, *.wav`), 사용자가 올린 참고 영상은 커밋하지 않습니다. 완성된 쇼츠 mp4 와 UPLOAD_INFO.md 는 `Downloads/` 에 커밋합니다.
* 대시 기호("—", "-")는 영상 문구, 설명, 채팅 답변에서 쓰지 않습니다. 쉼표와 마침표로 씁니다.
* 커밋 메시지와 산출물에 모델 이름을 쓰지 않습니다. 커밋 서명 줄은 그 세션의 안내를 따릅니다.
* PR 은 사용자가 요청할 때만 만듭니다.

## 2-1. 2026-09-30 오너 결정과 새 도구
* 오너 방침: 다른 수익화 채널처럼 원 채널 크레딧과 "All rights go to the owners" 표기로 편집 영상을 만들고, 좋은 것은 오너가 DM 으로 허락을 받는다. David Goggins 는 자기 영상 편집을 허용했다고 오너가 전함. 표기 문구 자체는 권리를 주지 않음 (Content ID, 수익 이전, 스트라이크 위험은 오너가 알고 결정).
* 위험 줄이기: 원본을 길게 그대로 쓰지 않기, 짧게 잘라 재구성 (정보 자막, 순위, 스토리, 리프레이밍), 원 채널 링크 크레딧, 음악은 업로드 때 유튜브 보관함.
* 소스 사이트: Bilibili 는 이 환경에서 720p 까지 받아짐 (`yt-dlp "bilisearch10:키워드"` 는 가끔 412). archive.org, Vimeo, X, TikTok, Instagram, Reddit 접속됨. 유튜브 스트림은 여전히 봇 확인으로 막힘 (쿠키를 쓰는 자동 다운로드는 이 환경의 권한 검사에서 거부됨, 2026-09-30). 유튜브는 오너가 yt-dlp 로 받아 드라이브에 올리는 방식 유지 (여러 개는 `yt-dlp -a links.txt -N 8`).
* 효과음: 드라이브 "자주쓰는 효과음" (1EKM0f9Q1x9010UZtuTwshZDgZsgJgiyL). 묵직한 것만 `assets/sfx_owner/ow_*.wav` 로 변환: `ow:boom` (저음 52%), `ow:transition` (42%), `ow:punch`, `ow:whoosh`, `ow:riser1`, `ow:riser8`. 가벼운 소리 16개(뾰로롱, 띠딩, 카툰 팝, 박수, 뿅 등)는 RageStyles 에 쓰지 않음. 과용 금지. git 제외.
* 자막: w1 의 네온 글로우는 어색하다는 평. 기존 TikTok Sans 흰 글씨 검정 테두리로. 도파민 효과(줌 펀치, 밝기, 쿵)는 계속.
* 새 효과 `dim_in` (샷 키 `{hold, dur, from}`): 영상 첫 장면이 거의 까맣다가 순간 밝아짐. 오너가 가끔 쓰면 효과적이라고 함. 제목 글자는 어두워지지 않음.
* 새 형식 참고: Goggins 쇼츠 (DailyMotivationDosis): 흰 바에 검정 설명 자막, 가로 영상, 빨간 화살표 (`meme` 레이아웃 + `arrow`). 주제 후보: Bodybuilders in Suits (1999 Mr. Olympia 클립), Eddie Hall (giantslivestrongman 클립 사용 채널 예시 hardcore_motivat1on).

## 2-2. 지금 하던 일 (2026-09-30 기준, 새 세션은 여기서 시작)
* 다음 영상 3개 (오너 요청): 1) Bodybuilders in Suits (1999 Mr. Olympia 클립), 2) Eddie Hall 500kg (원본 dFABFdd7nG4 의 Bilibili 재업로드), 3) David Goggins 이야기 (참고 형식: DailyMotivationDosis 의 흰 바 자막 + 빨간 화살표). 모티베이션 느낌, 도파민 효과 많이, 무거운 효과음만, 기존 자막 스타일 (글로우 금지), 가끔 `dim_in`.
* 결과물만 오너에게: 소스 검색, 다운로드, 편집까지 Claude 가 직접.
* Bilibili 소스 (work/ 는 커밋 안 되니 새 세션에서 다시 받기):
  `yt-dlp -N 8 -f "bv*[height<=1080][vcodec^=avc1]+ba/bv*[height<=1080]+ba/b" --merge-output-format mp4 --write-info-json -o "work/bili/%(id)s.%(ext)s" https://www.bilibili.com/video/<BV>`
  * BV1Vq4y127ww: Mister Olympia 1999 전체 (88분), BV1KT4y1Z74h: 1999 올림피아 현장 (19분), BV1YJ411g7e2: 숀 레이 1999, BV16Y411n7zj: 마이크 마타라조 1999
  * BV1Yi4y1t7oU: Eddie Hall 500kg + 경기 후 인터뷰 (10분, 1080p, 원본 youtube dFABFdd7nG4), BV1vt411x7Jh: 500kg 25초
  * Goggins: BV1dT4y1q7C3 (12분, 중국어 자막이 박혀 있을 수 있음, 확인), BV1uy411e7st (1시간 달리기 훈화, 중영 자막)
* Bilibili 검색: yt-dlp 의 bilisearch 는 412 가 자주 남. 대신 홈페이지 방문으로 받은 익명 쿠키(buvid3)로 `https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword=...` 호출 (Referer https://search.bilibili.com/). 결과 bvid, duration, play, title, author.
* 유튜브 쿠키 다운로드: 오너가 저장소 `.claude/settings.json` 에 `Bash(bash ragestyles-shorts/tools/yt_batch.sh:*)` 허락 규칙을 넣었고 (커밋 daa2877), 환경 변수 `YT_COOKIES_B64` (안 쓰는 계정 cookies.txt 의 base64) 를 넣었다고 함. 새 세션에서 `tools/yt_batch.sh` 를 만든다: 인자로 링크 목록 파일이나 URL 들, `YT_COOKIES_B64` 가 있으면 mktemp (chmod 600) 로 풀어 `--cookies`, 끝나면 trap 으로 삭제, `xargs -P 3` 병렬, `-N 8`, 1080p mp4, `--write-info-json`, 출력 `work/youtube/%(id)s.%(ext)s`. 반드시 `bash ragestyles-shorts/tools/yt_batch.sh ...` 형태로 저장소 루트에서 실행 (허락 규칙과 일치). 쿠키 값은 절대 출력, 커밋, 채팅 금지. 서버 IP 가 막히면 오너에게 알림.
* 업로드 자동화 (다음 목표): 메인 채널은 YouTube Data API v3 + OAuth (쿠키와 별개). 오너가 Google Cloud 프로젝트, OAuth 클라이언트, refresh token 을 환경 변수로 준비해야 함. 검증 안 된 API 프로젝트로 올린 영상은 비공개로 잠김 (감사 통과 전까지), 기본 쿼터 videos.insert 하루 100개.
* 드라이브: 소스 폴더 RageStyles YT1 (1-aIni1GNxG_GN87xXH6mFYgXkkoYW4Eu), 효과음 폴더는 2-1 참고 (새 세션에서 gdown 으로 다시 받고 ow_*.wav 로 변환).

## 2-3. 2026-09-30 세션 결과 (새 세션은 2-2 대신 여기부터)
* 만든 영상: `Downloads/new14/` s1 (1999 올림피아 정장 기자회견), e1 (에디 홀 500kg, 스컬 엔딩), d1 (고긴스 297 lbs 에서 네이비 씰, 흰 카드 형식). 빌드 스크립트 `plans10/build_s1.py`, `build_e1.py`, `build_d1.py`, 공용 `plans10/rscommon.py` (hit = 줌 펀치 + 밝기 + `ow:boom`, `sound()` 는 효과음 임팩트 위치 `PEAK` 에 맞춰 배치, `vox()` 는 Demucs 사본에서 원본 초로 소리를 가져옴). 오너 확인 전.
* 유튜브 다운로드 됨: `bash ragestyles-shorts/tools/yt_batch.sh links.txt` (저장소 루트에서, URL 또는 영상 ID 도 됨). `YT_COOKIES_B64` 를 mktemp(600) 에 풀고 끝나면 삭제, 쿠키 값은 출력하지 않음 (youtube 줄 수만 출력). n 챌린지에 Node 22 필요 (`/opt/node22/bin/node`, PATH 의 node 20 은 yt-dlp 가 거부) 와 `pip install "yt-dlp[default]"` (yt-dlp-ejs). 형식은 avc1 우선 (AV1 은 OpenCV 가 못 읽음). 대시로 시작하는 ID 는 파일 이름을 바꿔 씀 (`-K0chGkV0IE` → `K0chGkV0IE.mp4`).
* 원본 dFABFdd7nG4 (에디 홀) 는 유튜브에서 "unavailable". Giants Live 공식 다큐 -K0chGkV0IE (1080p, 클로즈업 많음, 음악 있어 Demucs) 를 씀. 같은 채널 T9Y4o_BqC0A 는 관중석 폰 촬영 가로 구도라 안 씀.
* 효과음 변환 규칙: 드라이브 13 BOOM → `ow_boom`, 12 화면전환 → `ow_transition`, 9 펀치 → `ow_punch`, 8 훅 → `ow_whoosh`, Riser 01/08 → `ow_riser1`/`ow_riser8` (48kHz 스테레오 wav). 임팩트 위치 boom 0.29초, punch 0.47, riser1 1.98, riser8 3.66, transition 0.96.
* 새 자막 스타일 `memebar` (bench.py): 흰 카드 위 검정 TikTok Sans ExtraBold 78, `*` 는 빨강. `layout` 은 `{"mode": "meme", "bg": [255,255,255], "box_aspect": 1.7778, "box_w": 1080, "box_y": 0.53}`, 화살표는 `marks` 의 `arrow` (tip 좌표).
* 1999 기자회견 이름표는 옆 사람 것일 때가 많음 (로니 앞에 "Jay Cutler" 이름표 등). 얼굴은 GETBIG.TV 영상의 이름 자막과 사회자 호명으로 확인. Mocvideo 결과 화면과 위키백과 순위가 다름 (륄 실격 반영 차이), 오너에게 알림.
* 환경 변수(`YT_COOKIES_B64` 포함)는 새 세션에서만 반영됨 (세션 도중에 바꾸면 그 세션은 옛 값). 자동 갱신은 이 환경에서 불가 (환경 변수를 세션 안에서 못 바꾸고 컨테이너는 끝나면 지워짐).
* 유튜브 쿠키가 같은 날 만료됨 ("cookies are no longer valid", 영상 데이터 403). 오너가 새로 내보내서 `YT_COOKIES_B64` 를 바꿔야 함. yt-dlp 위키 권장: 시크릿 창에서 로그인, youtube.com/robots.txt 를 연 상태에서 cookies.txt 내보내기, 그 창을 바로 닫기 (브라우저가 쿠키를 돌리지 않게). 쿠키 없이도 info.json 의 자막 URL 로 자막은 받아짐.
* 워드 바이 워드: `plans10/rscommon.py` 의 `Speech` (말 조각을 이어 붙이고 단어 시각을 출력 타임라인으로 옮김, 조각 끝에서 자막 끊김), `pipeline/wordcaps.py` (`palette=["*","~"]`, 문장 끝 넘어 합치지 않음), 스타일 `wordcap`. 단어는 faster-whisper medium.en 으로 다시 받아씀 (small 이 "five hundred kilo" 를 "farming to kill" 로 들음).
* 주의: CNBC 영상(X3yNsomAUvw)은 OpenCV 시크가 ffmpeg 보다 약 1.2초 늦게 읽음. 컨택트시트는 ffmpeg (`-ss` + `fps,tile`) 로 뽑아 확인.
* 다음: 오너 피드백 반영, 업로드 자동화 (2-2 마지막 항목).

## 2-4. 2026-09-30 4차 세션 결과
* 만든 영상: `Downloads/new17/` n1 Nick Walker (오너: "아주 좋아, 완벽한 수준", 이미 업로드), n2 Niall Darwen 클래식 (좋았다). Derek Lunsford 3위 편은 쓰지 말라고 해서 삭제. `Downloads/new18/` r1 Raul Flores 511kg, j1 15살 칼리스데닉스 3개 기록 (Andry Strong), s2 Sam Sulek Bulk Rebirth 27일차 20인치 팔. 빌드 스크립트 `plans11/build_*.py`, 공용 `plans11/newscommon.py` (`words()`, `speech()`, `Cutter.v/sync/until/hit_at`).
* 고화질 다운로드 링크 (오너 요청): CRF 12 원본을 `Downloads/hq/<id>_HQ.mp4` 로 커밋하고 푸시하면 `https://github.com/Sarahspick/sarahspick.github.io/raw/claude/optimistic-mendel-66zw8l/ragestyles-shorts/Downloads/hq/<id>_HQ.mp4` 로 받을 수 있음 (50MB 넘으면 GitHub 가 경고만 하고 받아줌, 100MB 넘으면 거절). 채팅에는 HEVC 28MB 본 (`tools/fit_send_hevc.sh`).
* 자막 위치: 클로즈업에서 얼굴이 박스 위쪽 절반을 채우므로 단어 자막은 y 0.68 to 0.7, 정보 자막은 y 0.86 (w1 첫 렌더에서 y 0.5 자막이 미치 얼굴을 가려서 고침). `newscommon.words()` 는 whisper 가 쪼갠 토큰 ("pre" "-workout", "$20" ",000", "125" "%") 을 다시 붙임.
* 7개 단위 작업 (오너 요청, 2026-10-02): 업로드와 예약은 오너가 직접 함. 7개마다 고화질 링크 7개 + 텍스트 파일 하나 (`Downloads/batchNN/UPLOAD_ALL.txt`, 영상별 [제목] [설명] [태그] [댓글]) 를 줌. 첫 묶음 batch01 = c1, mp1, t1, b1, w1, w2, w3. 유튜브 음악 (오디오 라이브러리, 쇼츠 사운드) 은 Data API 로 넣을 수 없음: 앱이나 스튜디오에서 오너가 직접 넣어야 함.
* 업로드 문구: 영상마다 `Downloads/<폴더>/UPLOAD_INFO.md` 에 제목, 설명, 태그, 해시태그를 쓰고 채팅으로도 보냄 (오너 요청).
* 유튜브 다운로드: 새 쿠키로 `tools/yt_batch.sh` 정상. 77분짜리 OlympiaTV Cq7TbOxcwPc 만 영상 데이터 403 (세 번 재시도해도 같음). 긴 영상은 PO 토큰이 필요한 것으로 보임.
* 계속 받는 방법 (제안): 1) 쿠키 수명: 안 쓰는 계정으로 시크릿 창 로그인, youtube.com/robots.txt 에서 cookies.txt 내보내고 창 닫기 (브라우저가 쿠키를 돌리지 않게). 이 환경은 세션마다 IP 가 바뀌므로 몇 주 단위로 교체 예상. 2) PO 토큰 공급자 `bgutil-ytdlp-pot-provider` (yt-dlp 플러그인, Node 스크립트 모드) 를 setup.sh 에 넣으면 긴 영상 403 과 쿠키 의존이 줄어듦 (아직 시험 안 함, github.com releases 가 막혀 있어 pip/npm 경로로 설치해야 함). 3) 쿠키가 막히면 대체: 오너 PC 에서 `yt-dlp -a links.txt` + rclone 으로 드라이브 폴더에 자동 업로드, 세션은 gdown 으로 받기. 4) 한 세션에 수십 개씩 받지 않기 (`--sleep-requests 1` 권장).
* 원본 음악: 소스에 음악이 깔린 구간 (Andry Strong 도전 장면, Sulek 차 안 토크, Giants Live 경기장) 은 Demucs vocals 만 씀. 검사: `no_vocals.wav` 의 mean_volume 이 -40dB 보다 크면 음악 있음.
* 자막 주의: 카운트 영상에서 코치가 끝자리만 셀 때 ("one, two" = 41, 42) 는 그 단어를 자막에서 빼고 화면 카운터를 보여줌 (j1). 욕설 구간은 조각에서 뺌.
* 업로드 자동화 준비: 오너가 환경 변수 `RS` 에 YouTube OAuth refresh token 을 넣어둠 (값은 절대 출력하지 않기). 다음 목표: Data API v3 videos.insert 로 비공개 업로드 스크립트 (클라이언트 ID, 시크릿도 필요한지 오너와 확인).

## 3. 채널 오너 취향 (시간순으로 쌓인 피드백, 아래쪽이 최신)

콘텐츠
* 실제 1:1 대결, 스토리가 있는 콘텐츠. 서로 관련 없는 영상 두 개를 이어 붙이는 것은 안 됩니다.
* 유명인(예: 우사인 볼트)과 시청자가 많은 나라(미국, 러시아, 유럽, 아시아) 중심. "자메이카 vs 남아공" 같은 건 아무도 관심 없습니다.
* 1900년대 옛날 영상은 좋습니다. 사람들이 처음 보는 영상이라서요.
* NASA 운동 영상은 매우 좋습니다 (c2 극찬). 하지만 NASA 사람들이 노는 영상(아폴로 "having fun")은 방향이 아닙니다.
* 군대 영상(미군 DVIDS)은 채널 방향이 아닙니다.
* 가끔 팩트체크를 합니다 (예: 샌도우 영상은 에디슨 본인이 아니라 에디슨 스튜디오가 촬영).
* (2026-09-29) 채널이 옛날 영상, NASA, 미군 영상 천지가 되는 건 싫다. 최신 영상, 트렌드한 운동, 헬스, 스포츠 영상을 쓴다. 옛날 영상은 가끔만.
* (2026-09-29) 자막은 장면과 정확히 맞아야 합니다. 1949 영상의 "NO HANDS" 가 틀렸다고 지적받았고, 확인해 보니 HUMAN THROW, 3 MAN TOWER, CARTWHEEL 도 틀렸습니다. 자막을 쓰기 전에 샷마다 프레임을 뽑아 동작을 확인합니다.

편집
* 첫 프레임에 제목과 자막이 이미 보여야 합니다 (첫 프레임이 썸네일이 되는 경우 대비). 렌더러가 t=0 자막은 페이드 없이 바로 그립니다.
* 2~4초마다 컷. 지루한 구간이 없어야 합니다 ("도파민").
* (2026-09-29) 같은 테이크 안에서 줌 배율을 바꿔 자르는 리프레이밍 컷은 부자연스럽다 (c4 v2). 대신 중요한 순간(포즈)에만 천천히 부드럽게 줌인하고 (`path` 키프레임), 지루한 시간(몸 돌리기 등)을 건너뛰는 컷을 씁니다 (c4 v3 참고).
* 원본 소리가 우선이고 끝까지 이어져야 합니다. c7 v1 은 14.5초 이후가 무음이라 지적받았습니다. `qa.py` 가 1.5초 이상 무음을 경고합니다. 무성 영화는 예외 (업로드 때 음악).
* 효과음은 최소한. 직접 합성한 효과음(라이저, 제트기 소리)은 이상하다는 평가. 전환 휘시 정도는 괜찮고, 쓸 때는 Mixkit 같은 실제 음원을 씁니다.
* 흔들림, 글리치, 과한 효과 금지. 프로필 배지 금지 (사람들이 클릭 안 함).
* 배경: 같은 영상을 크게 늘려 블러 처리하고 어둡게 한 것이 최고. 검정이나 흰색 단색 배경은 싫어합니다. 원본이 어두운 영상은 `darken` 을 0.8~0.95 로 올립니다.
* 영상 비율: 1:1 (또는 조금 더 세로). 4:3 은 영상이 작아 보여서 안 됩니다. 2:3 처럼 긴 비율은 자막 자리가 유튜브 UI 에 가려지므로 `box_w` 를 줄여서 씁니다 (예: 4:5 는 `"box_aspect": 0.8, "box_w": 880`).
* 제목은 위쪽(영상 박스 바로 위) 위치가 좋다고 했습니다. 자막은 영상 바로 아래.
* ~~폰트 Dela Gothic One, 노랑→주황 그라데이션 강조~~ (2026-09-29 교체됨).
* (2026-09-29) 폰트는 TikTok Sans (40M 조회수 쇼츠 61개 표지 분석에서 가장 많은 틱톡 기본 자막체 계열, BENCHMARK.md 참고). 자막 ExtraBold, 제목 Black, 흰 글자에 검정 테두리.
* ~~(2026-09-29) 참고 쇼츠의 "스컬 엔딩" 이 좋다고 함~~ (2026-09-30 취소: 💀 엔딩은 절대 쓰지 않음, 아래 참고): 마지막 순간 💀 가 아래에서 날아 올라오고, 휘핑 블러 뒤 마지막 프레임이 흑백으로 멈춰 어두워지고 비네팅, 제목은 사라지고 💀 만 약 3초. 플랜 키는 5장 참고 (`still`, `bw`, `vid_darken`, `vignette`, `whip_in`, 자막 `anim: rise`).
* (2026-09-29) 강조색은 그라데이션 하나가 아니라 노랑(`*단어*`, 255,214,0)과 주황(`~단어~`, 255,128,0)을 따로따로 씁니다.
* (2026-09-29, g1 피드백) 가로로 넓게 찍힌 동작(바벨 헤드 프레스처럼 옆으로 긴 구도)은 쇼츠에 안 맞아서 버렸습니다. 세로 9:16 으로 사람에게 초점을 맞출 수 있는 소스를 고릅니다.
* (2026-09-29, g1 피드백) 정보, 스토리텔링, 콘텐츠가 있어야 합니다. 대결이면 "Current Weight: 275 LBS", 누가 몇 kg 에서 실패했는지 같은 진행 상황을 텍스트로 계속 업데이트합니다 (화면 왼쪽이나 아래 고정 정보 패널).
* (2026-09-29) 미스터 올림피아 같은 최신 대회 영상은 매우 좋다는 평. 영상 여러 개로 나눠 만들어도 됩니다.
* (2026-09-29, o1 피드백) 영상 안에 없는 정보(예: 4위, 2위 상금)는 비워두지 말고 웹 검색으로 찾아서 채웁니다. 영상과 기사가 다르면 알려주고 영상(현장 발표)을 우선합니다.
* (2026-09-29, o1 피드백) 순위표는 검정 상자 없이 글자만 (테두리와 그림자), 화면 왼쪽, 세로 40% 지점이 중심. 바뀌는 큰 자막은 ~~화면 가운데 아래쪽 (y 0.70)~~ 너무 아래라서 정중앙 살짝 아래 (y 0.56). 글자가 화면을 너무 가리면 안 되므로, 결과가 다 나오고 1~2초 뒤에 순위표를 없앱니다.
* (2026-09-29, o1 v3) 순위표도 영상을 너무 가려서 뺐습니다. 화면 글자는 위 제목과 가운데 아래 자막 두 개만, 깔끔하게. 정보는 자막에 ("TONIO BURTON $30,000"). 발표 순간에는 빠른 살짝 줌인(`punch`), 밝기 번쩍(`flash`), 쿵 효과음을 넣습니다 (심심하지 않게).
* (2026-09-29, o1 확정, "아주 잘했어") 다음 영상부터: 줌인과 밝기업은 o1 보다 조금 더 강하게 (punch zoom 1.12~1.15, flash amount 0.45~0.55), 자막은 정중앙 (y 0.50). o1 은 확정본, 더 편집하지 않음.

* (2026-09-30, new14 피드백) s1 은 그나마 괜찮음. e1 v1 은 못 씀: 따옴표 요약 자막("I DON'T REMEMBER DOING THE LIFT" 식)은 로봇한테 전달받는 느낌, 스토리, 몰입, 감동 없음. 인물 대사가 있으면 그 말을 그대로 워드 바이 워드 자막으로 (요약 금지). 참고는 Peakzmotivation 에디 홀 쇼츠 (nLq6cJEAlO4 "Eddie Hall's secret that he used to lift 500 kilograms" 3,650만, KOkvPn9rbw4 "on the CONSEQUENCES" 730만): 38~41초, 한 사람 목소리가 처음부터 끝까지 이어지는 이야기, 얼굴이 화면을 채우는 클로즈업, 핵심 대사에 맞춰 리프트 장면, 자막은 1~3 단어.
* (2026-09-30) 💀 스컬 엔딩은 절대 하지 않음 (AI 편집으로는 캡컷만큼 안 나옴).
* (2026-09-30) d1 v1 의 도넛, 밀크셰이크 B롤은 짜침. B롤은 그 인물 자신(옛 사진, 훈련, 인터뷰)으로.
* (2026-09-30) 흰 배경 금지. 배경은 늘 블러, 영상 비율은 9:16(full) 또는 3:4 박스(`blur`, `box_aspect` 0.75)로 고정. 16:9 금지.
* (2026-09-30) 시작은 화면 전체가 0 에서 100% 로 약 1초 동안 밝아지게 (플랜 `open_fade`: 1.0, 자막과 제목은 처음부터 보임). 첫 컷은 1초 근처에서 넘김 (s1 v1 은 첫 샷이 2.6초라 지적).

* (2026-09-30, new15 피드백) d1 고긴스 v2 "아주 훌륭, 조금 옛날 영상이지만 편집이 매우매우 잘 됨, 이 방향으로" (한 사람 목소리 이야기 + 원문 워드 바이 워드 자막 + 본인 사진과 인터뷰 B롤 + 3:4 블러). s1 보디빌더도 "편집 잘했어". e1 에디 홀은 버림 (파일 삭제, 다시 만들지 않음).
* (2026-09-30, 아이폰 확인) 제목은 위 끝이 155px (캡션 키 `top`: 155), 영상 박스는 370px 부터 (3:4, `box_top` 370), 위쪽은 같은 영상 블러. `plans10/rscommon.py` 의 `Short.LAYOUT`, `TITLE_TOP` 이 기본값.
* (2026-09-30) 결과물은 채팅으로 바로 보냄 (모바일로 옮기기 편하게). SendUserFile 한도 30MB 라서 2패스 인코딩으로 29MB 안쪽에 맞춤 (`tools/fit_send.sh`).
* (2026-09-30, n1 피드백) 첫 1초가 가장 중요: 영상은 가장 고화질이고 시선을 확 끄는 장면으로 시작 (n1 은 저화질 폰 촬영 무대 장면으로 시작해서 지적, 3초쯤의 고화질 인터뷰로 시작했어야 함). 저음질 목소리 조각 ("I did it", 관중석 폰 녹음) 은 빼고 깨끗한 목소리부터. 화질을 늘 생각하기. 그래서 `open_fade` 는 0.25 정도로 짧게.
* (2026-09-30, n1 피드백) 사람 얼굴은 꼭 화면 안에. 줌 펀치나 크롭 때문에 머리가 박스 밖으로 나가면 안 됨 (n1 후반 무대 샷). 스틸 확인 때 얼굴이 잘린 컷은 cx, cy, zoom 을 고치거나 다른 구간으로 바꿈.
* (2026-09-30) 영상마다 제목, 설명, 태그를 텍스트 파일 (UPLOAD_INFO.md) 과 채팅 복붙용으로 같이 보냄.
* (2026-10-01) 제목: 설명형 제목 ("511 KG deadlift WORLD RECORD", "Day 27: 20 inch arms") 은 별로. 짧고 깔끔하게, 궁금하게, 바이럴 되게. 예: "The heaviest deadlift in history 🤯", "He's only 15 😳", "Sam Sulek is bulking again 💪". "Day 27" 같은 회차 표기 빼기. Gen Z 말투 ("Respect") 는 억지로 쓰지 않기. 화면 제목이 첫 자막과 같은 말을 반복하지 않게.
* (2026-10-01) s2 Sam Sulek 이 오히려 잘 나왔다는 평.
* (2026-10-01) 올림피아 5위에서 1위 카운트다운 (o1) 이 꽤 히트. 클래식판 c1 v1 (43초) 은 "너무 길고 지루하다". v2 (20초) 규칙: 0초에 5위 선수의 포즈 샷 + "5TH PLACE" 자막 0.5초, 0.5초에 컷과 동시에 사회자가 이름만 부름 + 줌 펀치 + 밝기 + 쿵 (설명 멘트 "the fifth place check for..." 빼기). 5, 4, 3위는 각 2초 안팎으로 빠르게. 뜬금없는 곁가지 ("presented by Thor") 빼고 깔끔하게. 첫 프레임이 제일 중요하니 open_fade 0. 머리가 자막에 가리지 않게 (가리는 샷만 자막 y 0.64~0.66).
* (2026-10-01, r1 다시 만들기) 오너가 1천만 조회 에디 홀 500kg 쇼츠 2개를 보냄 (저작권 때문에 커밋 안 함, work/ref/). "효과 더 주고, 더 보는 맛이 있게. 1천만 조회 쇼츠의 편집법을 배워서 적용." 분석:
  * A (스토리형, 33초): 컷 1~2초, 얼굴 극단 클로즈업 (화면을 얼굴이 꽉 채움), 핵심 단어에 빨강/주황 색 번쩍, 힘쓰는 동안 얼굴로 천천히 밀고 들어감, 클라이맥스에 RGB 분리 (색수차), 작은 대문자 자막 1~3단어 + 장면 설명 이탤릭 자막 "*half ton attempt*", "*wife is in shock*", 끝은 아내 반응 컷.
  * B (긴장형, 58초): 같은 리프트를 여러 각도로 이어 붙임 (정면, 측면, 바닥 낮은 각도, 얼굴 클로즈업), 리프트 도중 아내 반응 컷, 락아웃 후 환호를 길게 붙잡음.
  * 적용 (r1 v2, `plans11/build_r1.py`): 리프트를 실시간 소리 위에 정면 중계, 하프토르 채널 측면, 관중석 폰 (511kg 표지판), 코치 반응, 락아웃 슬로모션 얼굴 클로즈업 순으로 컷. `big_hit()` = 줌 펀치 + 밝기 + 빨강 워시 (`tint`) + 색수차 (`rgb`) + 쿵. 이탤릭 장면 자막 `act()` ("*Thor's record: 510 kg*", "*his coach*", "*Thor raises his hand*"), 얼굴 천천히 밀기 (`path`), 끝은 환호. 같은 사건의 다른 각도 영상을 꼭 같이 찾아 받기 (유튜브 검색 결과의 공식, 선수 본인 채널, 관중 폰 영상).
  * bench.py 새 효과: 샷 키 `tint` `[{at, dur, amount, color, hold}]` (색 워시), `rgb` `[{at, dur, px}]` (색수차). `speed: 0.5` + `interp: true` 슬로모션.
  * 자막이 얼굴을 가리지 않게: 화면 정중앙 (y 0.5) 자막 자리에 얼굴이 오면 cy 를 올려 얼굴을 박스 위쪽으로.

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
| new7 c4 v2, c7 v2 | 새 스타일 적용본 (블러 배경, 1:1, Dela Gothic One, 자막 영상 아래, c7 은 끝까지 원본 소리) | 폰트 교체 요청, 샌도우 줌 컷 부자연스러움, NO HANDS 틀림 |
| new8 c4 v3, c7 v3 | TikTok Sans, 노랑과 주황 강조 분리, 샌도우는 포즈 줌인과 시간 건너뛰기 컷, 1949 자막 전부 재확인 | 사용자 확인 전 |
| new10 t1, g1 skull | 스컬 엔딩 테스트: Pexels 캘리스데닉스 레벨 1~4, Gymshark 영상에 스컬 엔딩 | 사용자 확인 전 |
| new11 o1 | 2026 미스터 올림피아 결과 카운트다운 (9:16, 제목과 자막 하나, 발표마다 줌 펀치, 밝기, 쿵, `plans9/build_o1.py`) | 아주 훌륭함, 확정. 순위표는 화면을 가려서 뺌. 다음엔 효과 더 강하게, 자막 정중앙 |
| new13 w1 | 워드 바이 워드 모티베이션 첫 샘플 (닉 워커 우승 연설, 네온 글로우 키워드 자막 자동 생성) | 사용자 확인 전 |
| new12 o2~o5, g2 | 올림피아: 전 챔피언 3명 vs 닉, 톱10 카운트다운, 닉 워커 스토리, 다우다 1일차. Gymshark 썰매 대결 (결과는 각자 인터뷰 샷 위에) | 사용자 확인 전 |
| new14 s1, e1, d1 | 1999 올림피아 정장 기자회견, 에디 홀 500kg (스컬 엔딩), 고긴스 297 lbs 에서 씰 (흰 카드, 빨간 화살표) | s1 그나마 괜찮음 (첫 컷 느림). e1, d1 은 요약 자막, 짜친 B롤, 흰 배경, 16:9 로 못 씀 |
| new15 s1 v2, d1 v2 (e1 v2 삭제) | s1 첫 1초 페이드 + 1.2초 컷. d1 은 본인 목소리 이야기 + 원문 워드 바이 워드 자막 (`wordcap`), 3:4 블러 | d1 아주 훌륭 (이 방향), s1 잘함, e1 버림 |
| new16 s1 v3, d1 v3 | 제목 155px, 영상 박스 370px (3:4), 위쪽 블러 | 사용자 확인 전 |
| new17 n1, n2 | 닉 워커 올림피아 우승 (인터뷰 + 우승 연설), 니얼 다웬 클래식 우승 (5위에서 1위). Derek 3위 편은 오너 요청으로 삭제 | n1 아주 좋음, 완벽 (업로드함). 단 시작 1초 저화질, 후반 머리 잘림 지적. n2 좋음 |
| new18 r1, j1, s2 | 라울 플로레스 511kg (해설 + 통역 + 하프토르), 15살 칼리스데닉스 3개 기록, 샘 술렉 벌크 리버스 20인치 | 제목 전부 별로 (다시 지음). s2 가 오히려 잘 나옴. r1 은 1천만 조회 편집법으로 v2 다시 만듦 (확인 전) |
| new19 c1 | 클래식 올림피아 5위에서 1위 빠른 카운트다운 v2 (0초 5TH PLACE, 이름만, 줌 + 밝기 + 쿵) | v1 은 길고 지루하다는 피드백. v2 첫 컷 인물 오른쪽 치우침 수정 (cx 0.365), 고화질로 다시 |
| new20 mp1, t1, b1 | 맨즈 피지크, 212 결과 카운트다운, 티그스트 아세파 베를린 마라톤 | 사용자 확인 전 |
| new21 w1, w2, w3 | 세계 최강자 미첼 후퍼 vs 405 lb 벤치 (로니 콜먼), 프리워크아웃 통 블러프 (루크 엘스먼이 진실을 말하고 우승), 샘 술렉 올림피아 무대 (정장, 시상) | 사용자 확인 전 |
| new9 g1 | Gymshark 푸시 프레스 힘 대결, 범스테드 우승 후 카메라맨이 285 lbs | 내용은 좋지만 프레스가 가로 구도라 쇼츠에서 안 보임, 실패 무게 같은 정보 텍스트 부족. 폐기, 다시 만들지 않음 |

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

플랜 JSON (최신 예시는 `plans7/c7_1949_acrobatics_v3.json`, `plans7/c4_sandow_1894_v3.json`)
* `layout`: 생략하면 기본값 `{"mode": "blur", "box_aspect": 1.0, "box_top": 300}`. 키: `mode` (blur, meme, full), `box_aspect`, `box_top` (px), `box_y` (0~1 중심), `box_w`, `darken` (블러 배경 밝기, 기본 0.5), `bg` (meme 배경색).
* `shots[]`: `src` (`archive/Exercise1949` 처럼 `work/` 아래 경로, 확장자가 mp4 가 아니면 붙여 씀), `in`, `dur`, `speed`, `interp`, `zoom` (숫자 또는 [시작, 끝]), `cx`, `cy`, `ease`, `punch` ([{at, zoom, cx, cy, ramp, until}]), `audio` (원본 소리 사용), `af` (voice, film, ambience 필터), `audio_db`, `grade` ({sat, contrast, sharpen}), `bw`, `fade_in`, `fade_out`, 샷별 `layout`, `box_aspect`, `darken`, `still` (true 면 `in` 프레임을 멈춘 채로 dur 동안, 오디오는 그대로 이어짐), `vid_darken` (영상 박스 밝기, 스컬 엔딩 0.6~0.8), `vignette` (0~1), `whip_in` (샷 시작 모션 블러 초), `path` (카메라 키프레임 `[[샷 안의 초, zoom, cx, cy], ...]`, 구간마다 부드럽게 이어짐. 포즈에서만 줌인하고 나머지는 멈춰 있게 할 때 씀).
* `captions[]`: `t`, `d`, `text`, `style`, `anim` (기본 pop, 제목은 none, `rise` 는 화면 아래에서 날아 올라와 착지, 스컬 이모지용). 텍스트 문법: `*노랑 강조*`, `~주황 강조~`, `:flexed-biceps:` 같은 Noto 이모지 이름, `:flag-us:` 국기, `\n` 줄바꿈, `\*` 는 별표 그대로. 위치 덮어쓰기 `x`, `y` (0~1), 대상에 고정은 `shot` + `x`, `y`. 크기와 모양 덮어쓰기: size, color, font, italic, stroke, max_w, max_lines, align, line_gap, bg, pad, upper, shadow.
* 스타일: `title` (영상 위 제목), `cap` (영상 아래 자막), `big` (영상 아래 큰 대문자 라벨), `tag` (노랑 알약). 모두 TikTok Sans, 강조색은 `colors` (노랑, 주황). 예전 스타일 `title_dela`, `cap_dela` (Dela Gothic One 그라데이션), `sub`, `label`, `chapter`, `meme`, `top`, `action`, `list`, `story`, `big_anton`, `tag_old`, `title_old`.
* `marks[]`: `arrow` (빨간 화살표), `circle` (손그림 빨간 원, `shot` 기준 좌표), `progress` (n 개 중 k, 진행 바), `dim` (화면 어둡게).
* `marks[]` 의 `panel` (2026-09-29 추가, 오너 요청 정보 패널): `{"type": "panel", "t", "d", "x", "y" (왼쪽 위 모서리, 0~1), "w" (px), "size", "header", "rows": [{"t": 나타나는 시각, "text": "5TH  TONIO BURTON  *$30K*"}]}`. 어두운 반투명 상자에 줄이 하나씩 쌓입니다. 순위표, 현재 무게, 기록판에 씁니다.
* 9:16 `full` 레이아웃에서 자막 위치는 `y` 로 직접 줍니다 (big 기본 위치는 박스 아래라 화면 밖). o1 은 제목 y 0.085, 큰 자막 y 0.56, 패널은 `yc` 0.40 (전체 높이의 중심), `alpha` 0 (상자 없음), `stroke` 6, `shadow` true, `fade_out`.
* 플랜을 손으로 고치기보다 `plans9/build_o1.py` 처럼 빌드 스크립트로 만들면 샷 길이를 바꿔도 자막, 패널, 오디오 시각이 같이 따라갑니다.
* `audio_clips[]`: 다른 샷 위에 원본 소리를 까는 J컷. `{src, in, dur, t, af, db, fade}`.
* `sfx[]`: `{t, name, db, in}` (`in` 은 효과음 앞부분을 건너뛰는 초. `mk:788_big_cinematic_impact` 는 임팩트가 2.12초, `mk:2908_movie_trailer_epic_impact` 는 0.7초에 있어서 `in` 없이 쓰면 늦게 터집니다).
* 샷의 `flash`: `[{at, amount, dur}]` 발표 순간 밝기를 올렸다가 빠르게 되돌림. `punch` 와 같이 쓰면 "쿵" 느낌. `mk:` 로 시작하면 Mixkit (`mk:1143_cinematic_whoosh_deep_impact`), 아니면 `assets/sfx/` 합성음 (오너가 싫어하니 쓰지 않기).
* `lufs`: 목표 라운드니스 (-14). 원본 소리가 없는 스톡 영상은 효과음만 커지지 않게 -20.

워드 바이 워드 모티베이션 스타일 (2026-09-30, 참고: Peakzmotivation 에디 홀 500kg 쇼츠, 영상 700개 채널)
* 형식: 인터뷰 목소리 + 1~4단어 자막, 그룹마다 키워드 하나를 네온 색으로 (`~` 빨강, `^` 초록, `+` 하늘, `%` 보라, `*` 노랑), 글로우, 핵심 단어에 punch + flash + 쿵, 말 내용에 맞는 B롤.
* 자막 스타일 `word` (bench.py, TikTok Sans ExtraBold 88, glow 18). 새 색 표시 `+` `%` 는 render.py parse_tokens.
* `pipeline/wordcaps.py`: whisper 단어 타임스탬프 → 캡션 목록 자동 (구 단위 묶기, 키워드 자동 선택, `force`/`skip`). 예시 `plans9/build_w1.py` (말 조각을 이어 붙이고 단어 시각을 출력 타임라인으로 옮김).
* 참고 영상 채널은 팟캐스트와 WSM 중계를 무단 사용. 우리는 형식만, 소스는 CC BY 등 합법만.
* CapCut 연결: 공식 API 없음. 오픈소스 VectCutAPI (github.com/sun-guannan/VectCutAPI) 가 CapCut 드래프트(draft_content.json)를 만들 수 있고, 오너 PC 의 CapCut 에서 열어 내보내기. 클라우드에서는 CapCut 실행 불가. 우선순위는 우리 렌더러 자동화, CapCut 은 선택.

기타 도구
* 대사 받아쓰기: faster-whisper `small.en` 또는 `medium.en`, `word_timestamps=True` 로 컷 지점을 단어 경계에 맞춥니다 (c7 v1 은 "fitness" 중간에서 잘렸던 것을 v2 에서 고침).
* 음악 제거: Demucs htdemucs (`python3 -m demucs --repo work/models/demucs -n htdemucs --two-stems vocals`). 가중치는 dl.fbaipublicfiles.com 이 막혀 있어 Hugging Face 미러를 씁니다.
* 음악 섞임 검사: panns_inference (선택).
* 소스 찾기: `python3 tools/commons_search.py out.json "strongman" "deadlift"` (Wikimedia Commons 영상, 라이선스 포함), `python3 tools/youtube_cc_search.py "deadlift world record"` (유튜브 CC 라이선스 영상 검색 결과만, 다운로드는 안 됨), `python3 tools/youtube_license_check.py <ID>` (영상 페이지의 라이선스 문구 확인, 봇 페이지면 unknown).
* 스톡 영상: `python3 tools/stock_search.py search "deadlift" "boxing training" --portrait` 후 `python3 tools/stock_search.py get pexels:<id> pixabay:<id>` → `work/stock/`, 작가와 라이선스는 `work/stock/credits.json` 에 기록.
* 폰트 분석 방법: 쇼츠 세로 표지 `i.ytimg.com/vi/<id>/oardefault.jpg` (1080x1920) 와 `oar1.jpg`, `oar2.jpg` 프레임을 받아 봅니다.
* 받아쓴 대사: `sources/transcripts/` (Exercise1949 전체 대사, 초 단위).
* 브라우저: Playwright 크로미움은 `/opt/pw-browsers` 에 있음. 프록시 인증서를 NSS 에 먼저 등록해야 합니다: `certutil -A -d sql:/root/.pki/nssdb -t "C,," -n ccr-agent-proxy -i /root/.ccr/agent-proxy-ca.crt`.

유튜브 CC BY 영상 받는 방법 (2026-09-29 확정)
* 오너가 자기 컴퓨터에서 yt-dlp 로 받습니다: `yt-dlp --cookies-from-browser firefox -f "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080]" --merge-output-format mp4 -o "%(id)s.%(ext)s" <URL>`. 윈도우 크롬은 쿠키 DB 잠금과 새 암호화 때문에 실패하니 파이어폭스를 씁니다. nsig 에러가 나면 `yt-dlp -U` 와 Deno 설치. 쿠키는 이 환경으로 절대 가져오지 않습니다.
* 채팅은 30MB 제한이라 구글 드라이브 공유 폴더로 넘깁니다: 내 드라이브 > Claude Youtube Project (https://drive.google.com/drive/folders/15ZuFnwkci3M4oeBMUKKiSUU5VHzC-RkW, 링크 공유) > 세션별 폴더 (이번 세션은 RageStyles YT1). 드라이브의 다른 폴더와 문서는 열지 않습니다.
* 폴더 목록: `curl -sL "https://drive.google.com/embeddedfolderview?id=<폴더ID>"` 에서 파일 이름과 ID 를 읽고, `python3 -m gdown <파일ID> -O work/youtube/<ID>.mp4` 로 받습니다 (pip install gdown).
* 받은 영상은 `work/youtube/` (커밋 안 함). 배경음악은 Demucs 로 필요한 구간만 분리해서 `work/youtube/gs_vox.mp4` 처럼 목소리와 함성만 남긴 파일을 만들어 씁니다 (plans8 참고, `in` 은 그 구간 기준).

## 6. 소스별 메모

* Internet Archive (Prelinger, Coronet 교육영화, 에디슨 필름, 1910 복싱): 퍼블릭 도메인. 설명란에 출처 표기.
* NASA (images.nasa.gov): 저작권 없음. 크레딧 NASA, "NASA 가 채널을 보증하지 않음" 문구 권장.
* Wikimedia Commons: CC BY / BY-SA. 저자와 라이선스를 설명란에 반드시 표기. BY-SA 소스를 쓰면 그 영상도 BY-SA 로 표기. `safp_100m` 은 TV 중계 캡처라 권리가 불확실하므로 쓰지 않습니다. upload.wikimedia.org 는 429 제한이 심해서 한 번 시도 후 4~5분 쉬기.
* Mixkit 효과음: 상업적 유튜브 사용 가능, 표기 불필요, 파일 자체 재배포 금지 (그래서 git 에서 뺐습니다. 예전 커밋 기록에는 남아 있습니다).
* DVIDS: 미군 영상, 방향이 아니라 보류. 쓸 경우 "The appearance of U.S. Department of War (DoW) visual information does not imply or constitute DoW endorsement." 문구 필수.
* 막힌 곳: 유튜브 영상 스트림(googlevideo.com, 2026-09-29 재확인: 봇 확인, 쿠키 없이는 불가라 우회하지 않음), dl.fbaipublicfiles.com, github.com releases, Pexels 와 Pixabay 웹사이트 (Cloudflare 확인 페이지).
* Pexels, Pixabay API: api.pexels.com, pixabay.com/api 는 접속됩니다 (키 필요). Pixabay 파일 서버 cdn.pixabay.com 은 데이터센터 IP 에 Cloudflare 확인을 띄울 수 있어서, 그러면 도구가 알리고 멈춥니다.
* 유튜브 CC BY: 업로더가 권리를 가진 경우에만 유효. 후보와 크레딧 형식은 `sources/cc_youtube_candidates.md`.
* ViralHog: 약관상 라이선스 없이 다운로드나 사용 금지. 견적은 licensing@viralhog.com 메일로만 (`sources/viralhog_license_request.md` 초안). 라이선스를 산 파일만 씁니다.

## 7. 더 재미있는 영상을 구하는 방법

2026-09-29 기준 우선순위: 최신 영상이 먼저입니다.
1. 유튜브 CC BY (브랜드, 협회, 선수 본인 채널): 목록은 `sources/cc_youtube_candidates.md`. 오너가 받아서 채팅에 올리면 편집.
2. Pexels, Pixabay API (`tools/stock_search.py`): 합법이고 최신이지만 스토리가 약하니, 대결, 랭킹, 팁 같은 구성으로 가치를 만듭니다.
3. ViralHog 등 바이럴 영상 업체: 라이선스를 산 뒤에만.
4. 원작자 허락, 직접 촬영.
5. 옛날 퍼블릭 도메인 영상과 NASA 는 가끔만.

아래는 이전(질문 8) 답변 기록입니다.

1. 유명 선수가 나오는 옛 뉴스릴과 스포츠 필름: Universal Newsreel (1929~1967, 유니버설이 미국 국립문서보관소에 기증한 뒤 퍼블릭 도메인으로 알려짐, 소리 있음), 1930년 이전에 공개된 미국 필름(공개 후 95년이 지나 퍼블릭 도메인), 미국 의회도서관의 초기 필름. 조 루이스, 베이브 루스, 잭 뎀프시 같은 유명인이 나옵니다. archive.org 에서 받을 수 있어 이 환경에서 바로 가능. 쓰기 전에 항목마다 권리 표기를 확인하고, 올림픽 경기 장면은 IOC 가 권리를 주장하니 뉴스릴이라도 피합니다.
2. CC BY 스포츠 영상: 유튜브 검색 필터의 Creative Commons (예: dt5nR7_CsbY, 파블로 나코네치니 505kg 데드리프트, CC BY 확인됨). 이 환경은 유튜브 다운로드가 막혀 있으니 같은 영상이 Wikimedia Commons 에 옮겨져 있는지 찾거나("From YouTube" 템플릿), 업로더에게 원본 파일을 받습니다.
3. 원작자 허락: 헬스 인플루언서, 스트롱맨, 지역 대회 채널에 DM 으로 크레딧 조건 사용 허락을 받고, 파일은 사용자가 채팅에 올립니다. 기존 규칙과 가장 잘 맞는 방법.
4. 유료 라이선스: ViralHog, Newsflare, Jukin Media(현 Trusted Media Brands), Storyful 같은 바이럴 영상 라이선스 업체. 가장 재미있는 영상이 많지만 비용이 들고 업체 표기 조건이 붙습니다.
5. 직접 촬영: 헬스장 챌린지, 1:1 대결을 오너가 찍어서 올리기.
6. 무료 스톡(Pexels, Pixabay, Mixkit 영상): 합법이지만 스토리가 약합니다. Pexels 와 Pixabay 는 여기서 막혀 있어 사용자가 받아서 올려야 합니다.
* 하지 말 것: 올림픽, 세계육상, UFC 같은 공식 중계 영상 재사용 (Content ID 와 저작권 경고).

## 8. 다음 아이디어 (방향에 맞는 것)

진행 중 (2026-09-29, 드라이브 RageStyles YT1 폴더의 Cq7TbOxcwPc.mp4, XlZZRCaETAs.mp4)
* 소스: "2026 Mr. Olympia Finals Official Footage", OlympiaTV (https://youtu.be/Cq7TbOxcwPc), 77분, 1080p30. OlympiaTV 다른 영상은 CC 필터에 나오지만 이 영상은 아직 안 나옴. 업로드 전에 오너가 설명란 라이선스 확인 필요.
* 구성: 0~30분 비교 심사(단체), 31~59분 선수별 개인 포징 루틴(한 명이 가운데, 9:16 에 최적), 1:00:10 탑10 포즈다운, 1:04~1:08 시상, 1:08 이후 탑3 메달, 우승 트로피, 인터뷰.
* 개인 루틴 시작: Chinedu Andrew Obiekea 31:40, Tonio Burton 35:10, Michal Krizanek 38:00, Regan Grimes 39:40, James Hollingshead 41:50, Behrooz Tabani 52:00, Nick Walker 54:37~56:05, Derek Lunsford 57:01~59:24.
* 결과 (대사로 확인, 초는 원본 기준): 5위 Tonio Burton 상금 $30,000 (~3855), 4위 Andrew Jacked (~3919), 3위 Derek Lunsford, 전 챔피언, 동메달 $100,000 (~4000), 마지막 둘 Samson Dauda 와 Nick Walker 가운데로 (~4074), 우승 Nick Walker, 금메달, 샌도우 트로피, $600,000, "2026 Mr. Olympia" (~4093~4125). 해설: "he defeated three former Mr. Olympia".
* 받아쓴 대사: `work/youtube/olyend_tr.txt` (3570초부터, 줄 앞 숫자에 3570 을 더함).
* 사람 추적: `tools/track_person.py` (torchvision 사람 검출, pip install torchvision --index-url https://download.pytorch.org/whl/cpu), 출력 path 를 shot 에 넣고 "ease": "linear".
* 주의 (2026-09-29): 우승 발표 직후 꽃가루 속에서 닉을 안는 초록 트렁크 선수는 Samson 이 아니라 Andrew Jacked (4위, 초록 트렁크, 이미 메달). o1 의 "2ND SAMSON DAUDA $200,000" 자막이 이 포옹 샷 위에 있음 (확정본이라 그대로, 오너에게 알림). 사람 이름 자막은 그 사람이 화면에 있는 샷에만.
* 2026 톱10 (fitnessvolt.com 결과, 무대 발표와 일치): 1 Nick Walker (미국), 2 Samson Dauda (영국), 3 Derek Lunsford (미국), 4 Andrew Jacked 본명 Chinedu Andrew Obiekea (UAE), 5 Tonio Burton (미국), 6 Michal Krizanek (슬로바키아), 7 Regan Grimes (캐나다), 8 Behrooz Tabani (이란), 9 Brandon Curry (미국), 10 James Hollingshead (영국). 역대 우승: 2019 Curry, 2023/2025 Lunsford, 2024 Dauda. 2025 결과: 1 Lunsford, 2 Choopan, 3 Andrew Jacked, 4 Dauda.
* 루틴 포즈 확인 시각 (원본 초, 0.5초 단위로 확인): Hollingshead 2577 FDB, Curry 2838 FDB, Tabani 3130 FDB, Grimes 2388.5 FDB, Krizanek 2304.5 BDB, Burton 2179.7 FDB, Andrew Jacked 1952.5 FDB, Lunsford 3513.7 BDB, Dauda 3056.7 FDB, Walker 3297 FDB (Walker 루틴: 3294 앞 광배, 3304.5 사이드 체스트, 3316.5 BDB, 3322 뒤 광배).
* `plans9/olycommon.py`: o2~o5 공용 (Short 클래스, hit = 줌 펀치 + 밝기 + 쿵). Demucs 본: `work/youtube/olyrt_vox.mp4` (1860~3580초), `oly_vox.mp4` (3840~4330초), `gs_sled_vox.mp4` (Gymshark 75~275초).
* Gymshark 썰매 (XlZZRCaETAs): 이름표와 결과판 얼굴로 확인. 1 Lucy Davis 하이브리드 0:56, 2 Samantha Cubbins 크로스핏 1:02, 3 Lea Schreiner 독일 파워리프터 (벤치 100kg) 1:04, 4 Oyinda 펑셔널 1:28, 5 Yazmin Stevens 역도 1:46.
* 쇼츠 계획: 1) 발표 카운트다운 (왼쪽 정보 패널에 5위부터 순위와 상금이 하나씩 쌓임, 마지막 1:1 Nick vs Samson, 우승 순간), 2) 새 챔피언 Nick Walker 포징 루틴 (포즈 이름은 프레임 확인 후), 3) 포즈다운 1:1 Nick vs Derek. Gymshark XlZZRCaETAs 는 여성 썰매 밀기/당기기 대결 (80kg, 100kg, 기록 01:04, 01:28, 01:46, 01:02, 00:56), 무게와 기록 패널로 만들기.

최신 영상 (2026-09-29 추가, 우선)
* 크리스 범스테드, 데이비드 레이드 등 짐샤크 스트렝스 테스트: 누가 제일 셀까 랭킹 (CTRL7o8iYgc).
* 래리 윌스 vs NFL 선수 225 벤치 대결 (-CfI_zQzwic).
* 2026 미스터 올림피아: 우승자 팩트체크 후 포즈다운 1:1 (OlympiaTV 공식, Ivan Bodybuilding).
* 16살이 깬 가장 오래된 파워리프팅 세계기록 (zsVGiAJOnNA, 미국).
* 팔씨름 전설 치플렌코프 명승부 (3bCXgJiQ0wA).

예전 아이디어 (옛날 영상, 가끔만)

* 조 루이스 vs 막스 슈멜링 1938 (미국 vs 독일, 1936 패배 후 1라운드 KO 복수극): Universal Newsreel 에서 찾기.
* 잭 뎀프시 vs 제스 윌러드 1919 (1라운드에만 다운 7번, 1919년 공개작이라 미국 퍼블릭 도메인): archive.org 에서 찾기.
* 1904 세인트루이스 올림픽 마라톤의 황당한 실화 (팩트체크 필수, 퍼블릭 도메인 사진이나 필름 필요).
* 1900년대 스트롱맨 (샌도우 후속, 의회도서관 필름).
* NASA 운동 2탄: ARED 스쿼트, 데드리프트 (`nasa_extra` 그룹 소스 이미 목록에 있음).
* 세계 최강의 사나이 아틀라스 스톤 (`wsm_stones`, CC BY 3.0).
* 유도 세계선수권 한판승 (`judo_2011`, CC BY 3.0, 에스토니아 vs 브라질이라 국가 흥미는 약함).
