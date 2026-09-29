# RageStyles 쇼츠 자동 편집 파이프라인

헬스/운동 주제 영어 쇼츠를 사람 개입 없이 만드는 스크립트. 첫 테스트: `01_1967_army_test` (42초, 1080x1920).

## 소스 원칙
- 실제 촬영 영상만 사용(AI 생성 영상 없음). 단, 남의 유튜브/틱톡 영상을 받아 쓰지 않고 **퍼블릭 도메인** 영상만 쓴다.
  미국 연방정부 제작물(국립기록원 NARA, archive.org의 FedFlix 컬렉션)은 저작권이 없어 수익화에 안전하다.
- 원본 오디오(필름 음악)는 쓰지 않는다. 음악과 효과음은 코드로 직접 합성해서 Content ID에 걸릴 일이 없다.
- 사실관계는 원본 필름 나레이션을 ElevenLabs STT로 받아써서 확인한 내용만 대본에 넣는다.

## 흐름
1. 소스 찾기: archive.org 검색 API (`mediatype:movies AND collection:FedFlix`, 키워드 physical fitness 등).
2. 컨택트 시트(ffmpeg tile)로 장면 타임코드 선정, 필요한 구간 나레이션을 STT로 전사해 사실 확인.
3. 대본 작성 → `python3 tts.py 01_1967_army_test` (Mark 목소리, 단어별 타임스탬프).
4. `render.py` 상단 SHOTS(대본 단어 → 원본 초)를 채우고 실행:
   `SHORT_DIR=01_1967_army_test SHORTS_WORK=<src/와 fonts/가 있는 폴더> python3 render.py --preview` 로 프레임 확인 후 `--preview` 빼고 본 렌더.

## 편집 스타일 (render.py가 하는 일)
- 문장 사이 무음 압축 + 1.06배속, 컷은 나레이션 단어에 맞춤(1.1~4초).
- 상단 고정 제목(흰색/노랑 2줄, Anton), 가운데 1:1 영상 창, 비네트, 대비/채도 보정.
- 컷마다 0.2초 펀치인 줌 + Ken Burns, 주요 전환에 흰색 플래시.
- 단어 단위 팝업 자막(말하는 단어와 키워드 노랑), 5칸 이벤트 진행바(시청 지속용), "500/500" 스탬프.
- 효과음: 컷마다 휘슉, 이벤트마다 딩, 첫 프레임과 스탬프에 붐, 마지막 질문 전 라이저. 96BPM 합성 비트를 깔고 -14 LUFS 정규화.
- 마지막 장면이 첫 장면(통나무)으로 돌아가 루프 시청을 유도하고, 질문으로 댓글을 유도한다.

## 준비물
`pip install numpy pillow imageio-ffmpeg`, 폰트 Anton / Montserrat 900 (OFL, jsDelivr fontsource), 환경변수 `ELEVENLABS_API_KEY`.
