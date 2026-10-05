# Peak ProMax 밈 채널 플레이북 (2026-10-05)

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

## 2. 채널 브랜딩 (2026-10-05 변경: Aura Receipts 폐기)
- 채널명: **Peak ProMax**. 소개 한 줄: "only peak clips. zero mid."
- 핸들: youtube.com/@peakpromax는 이미 "Peak Promax"라는 채널이 있음(본인 채널이 아니면 다른 핸들 필요). 비어 있는 후보: @peak.promax, @peakpromaxx (2026-10-05 확인). 영상 워터마크는 핸들 대신 채널명 "Peak ProMax".
- 프로필: 주황에서 빨강 그라데이션, 흰 산봉우리 삼각형 + PEAK. 48px에서도 읽힘.
- 배너: 검정 배경, PEAK(흰색) PROMAX(주황), 아래 한 줄 소개. 전부 모바일 안전 영역 안.
- 파일: brand/profile.png, brand/banner.png. 다시 만들기: `python3 make_brand.py`

## 3. 편집 템플릿
```
python3 meme_edit.py main.mp4 "New fear unlocked 🙏😭" -o out.mp4 \
    --reaction punchline.mp4 --pop "OH!@2.5" --start 0 --end 9
```
- 1080x1440, 흰 캡션 바, @AuraReceipts 워터마크, 선택 사항: "My honest reaction:" 펀치라인 클립, 지정한 초에 팝업 텍스트. 소리가 없는 클립은 무음 트랙을 넣음.
- 필요: ffmpeg, Pillow, Noto Color Emoji (fonts/에 Anton, Oswald, Roboto Condensed 포함, 모두 OFL)

## 4. 영상 소스와 유튜브 정책 (2026-10-05 변경)
- 다른 사람 영상을 쓰되, 그대로 다시 올리지 않고 우리 해석과 편집을 얹는다. 유튜브의 재사용 콘텐츠 정책은 "남의 영상 + 의미 있는 변형(코멘터리, 새 맥락, 편집)"은 수익화를 허용하고, "그대로 재업로드나 자막만 얹은 것"은 거절한다.
- 영상마다 반드시 들어갈 것 (peak_edit.py로 처리):
  1. 우리만의 캡션(농담 포인트). 장면 설명 말고 보는 사람의 속마음.
  2. 정지 화면 + 줌 + 빨간 동그라미와 화살표로 "여기 봐" 해설.
  3. 슬로모 리플레이 또는 펀치라인 클립("My honest reaction:")으로 새 맥락.
  4. 직접 합성한 효과음.
  5. 원작자 크레딧 "🎥 @원작자"를 화면과 설명란에.
- 피할 것: 다른 밈 채널이 이미 편집한 영상(캡션과 워터마크가 박힌 것), 영화와 스포츠 중계 원본(Content ID에 바로 걸림), 원본을 길게 그대로 쓰는 것. 원본 사용은 짧게, 우리 편집 비중은 높게.
- 원작자가 내려 달라고 하면 바로 내린다.

## 5. peak_edit.py (메인 편집기)
- 레시피(JSON)로 구간, 캡션, 정지 화면, 줌, 동그라미, 화살표, 팝 텍스트, 흔들림, 플래시, 슬로모, 효과음, 크레딧을 지정한다. 형식은 파일 맨 위 설명 참고.
- 실행: `pip install pillow numpy && python3 peak_edit.py recipes/파일.json`
- 가로 영상은 위아래를 흐린 배경으로 채움. 세로 영상은 꽉 채움.

## 6. 오리지널 애니메이션 (보조)
- 아우라 영수증 영상은 폐기 (2026-10-05).
- out/02_group_chat.mp4 (17초, 단톡방 피자 도둑): 남은 1개. 다시 만들기 `python3 video2_groupchat.py`
- anim.py, sfx.py는 peak_edit.py가 같이 씀.
