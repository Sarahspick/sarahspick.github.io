# Aura Receipts 밈 채널 플레이북 (2026-10-05)

## 1. 벤치마크: @ZobsterPrime
- 구독 66.5K, 누적 조회 4.11억, 영상 85개, 2020년 개설. 조회수는 몇 개 쇼츠에 몰려 있음: Magneto 71M, Each one got smarter 24M, Dad prank 13M, Everyone turned around 7.9M, national anthem 7.4M.
- 소개글에 "모든 영상을 내가 직접 편집한다, Premiere와 Photoshop을 쓰고 오디오는 YouTube Audio Library에서 가져온다"고 적어 둠. 유튜브 재사용 콘텐츠 심사를 의식한 문구로 보임.
- 포맷 (샘플 4개 분석):
  1. 3:4 세로 화면. 위쪽은 흰 바에 굵은 condensed 폰트로 검은 캡션을 넣고, 끝에 😭🙏 이모지. 아래가 영상.
  2. 캡션은 장면 설명이 아니라 시청자가 할 말을 대신 함 ("New fear unlocked", "To this day I still don't know what Dr. Strange did here", "It actually slowed down a little when he put his arm out").
  3. 펀치라인 클립을 붙임: 사고 장면 뒤에 "My honest reaction:"과 함께 비슷한 상황의 다른 클립(벤치에 깔린 남자).
  4. 효과음 팝업 "OH!", 빨간 화살표, 자막. 중앙 하단에 @ZobsterPrime 워터마크.
  5. 길이 9~19초, 반복 재생을 노린 짧은 컷.
- 제목 공식: 짧은 한 줄 + 😭/🥀/💔/✌️. 예) "Lost all of his aura instantly 🥀", "Bro moved the bike just in time 😭".

## 2. 채널 브랜딩
- 채널명: **Aura Receipts**, 핸들 **@AuraReceipts** (2026-10-05 기준 youtube.com/@aurareceipts는 404, 비어 있음)
- 한 줄 소개: "every clip, somebody pays."
- 컨셉: 영상마다 누가 아우라를 잃었는지 영수증 끊어 주는 채널. 캡션에 "-1000 aura" 같은 표현을 시그니처로 반복.
- 다른 후보 (모두 404 확인): Certified Huh (@certifiedhuh), Cooked Count (@cookedcount), Negative Aura 404 (@negativeaura404), Honest Reaction HQ (@honestreactionhq)
- 파일: brand/profile.png (800x800), brand/banner.png (2560x1440, 모바일 안전 영역 1546x423 안에 핵심 요소 배치. brand/banner_safe_area_preview.jpg의 초록 박스로 확인)
- 다시 만들기: `cd meme-channel && pip install pillow && python3 make_brand.py`

## 3. 편집 템플릿
```
python3 meme_edit.py main.mp4 "New fear unlocked 🙏😭" -o out.mp4 \
    --reaction punchline.mp4 --pop "OH!@2.5" --start 0 --end 9
```
- 1080x1440, 흰 캡션 바, @AuraReceipts 워터마크, 선택 사항: "My honest reaction:" 펀치라인 클립, 지정한 초에 팝업 텍스트. 소리가 없는 클립은 무음 트랙을 넣음.
- 필요: ffmpeg, Pillow, Noto Color Emoji (fonts/에 Anton, Oswald, Roboto Condensed 포함, 모두 OFL)

## 4. 영상 소스 규칙 (중요)
- 남이 X나 틱톡에 올린 영상을 받아서 다시 올리지 않는다. 저작권 침해이고, 이 저장소의 기존 규칙(허락받은 영상만, 다운로드 툴 우회 금지)과도 맞지 않는다. 유튜브에서는 Content ID 클레임, 3회 경고 시 채널 삭제, 재사용 콘텐츠 판정으로 수익화 거절로 이어진다.
- 쓸 수 있는 소스:
  1. 원작자에게 DM으로 허락받기. 바이럴 영상은 보통 Jukin, ViralHog, Newsflare 같은 라이선스 업체가 권리를 갖고 있어 소액으로 라이선스 가능. 허락 화면은 캡처해서 보관.
  2. 영상 하단 크레딧에 원작자 표기 (예: "🎥 @원작자 (used with permission)").
  3. 직접 찍은 리액션과 상황극, 직접 만든 펀치라인 클립. 채널만의 인사이트는 결국 캡션과 펀치라인 선택에서 나온다.
- 영상이 생기면 meme_edit.py로 하루 1~2개 편집.
