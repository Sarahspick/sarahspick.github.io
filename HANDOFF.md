# Sarah's Pick 인수인계 문서 (2026-09-16 밤 기준)

이 문서는 Claude가 다음 세션에서 그대로 이어서 일할 수 있도록 쓴 것. 사람(Mochi)과 Claude 둘 다 읽는 용도.

## 1. 사업 한 줄 요약
미국 타겟 인스타그램 계정 Sarah's Pick에 제품 숏폼을 하루 1개 올리고, bio 사이트(sarahspick.github.io)에서 아마존 제휴 링크로 연결해 수익을 내는 사업. 목표는 최대한 자동화.

## 2. 절대 규칙
- 영상은 직접 촬영했거나 원작자 허락을 받은 것만 쓴다. 무단 재업로드, 텍스트만 덮는 편집, 다운로드 툴 우회는 하지 않는다. Batch 1의 9개는 모두 허락받은 최종 편집본이라고 Mochi가 확인함. 편집은 Claude가 하지 않는다.
- 문구 규칙 (Mochi 지시): 대시 기호("—", "-") 절대 금지. 모든 문장은 20대 여성이 쓴 듯 짧고 감성적으로, 한 문장 또는 최대 두 문장, 이모지 적극 사용, 사람 느낌. 채팅 답변에도 대시 금지.
- 고정댓글 맨 끝에는 반드시 "As an Amazon Associate I earn from qualifying purchases." (아마존 약관). 캡션 해시태그에 #affiliate 포함 (FTC).
- 제휴 링크 형식: https://www.amazon.com/dp/ASIN?tag=hp302-20 (SiteStripe 불필요, 제3자 단축링크 금지).

## 3. 계정과 자산
- 아마존 어소시에이트 태그: hp302-20. 인스타 주소는 등록됨. 사이트 주소(https://sarahspick.github.io)도 등록 필요.
- 인스타그램: Sarah's Pick, 비즈니스 계정으로 전환 중. 핸들 가정값 @sarahspick (사이트에 이 링크가 박혀 있음. 실제 핸들이 다르면 build_site2.py의 IG 변수 수정).
- GitHub: 사용자 Sarahspick, 저장소 Sarahspick/sarahspick.github.io (공개, main 브랜치, 루트의 index.html이 사이트). 저장소를 세션 소스로 선택한 세션만 push 가능 (2026-09-16 소스 연결 세션에서 push 확인됨). main에 올리면 GitHub Pages가 1분 안에 자동 배포함 (Actions 탭의 "pages build and deployment"가 success면 반영 완료).
- 구글 드라이브 (hw54974875@gmail.com 계정, Claude 드라이브 커넥터 연결됨):
  - 작업 폴더 ID 1cJSARFOFkpssp5s4RfenM2eSp0dzPAtz (영상 9개 원본)
  - 출력 폴더 01_batch1_output ID 1_gF8h-GJMAJ5Yf2NXtG7AnNbcvtXmr9A (검수표 구글시트, 문구, 이 문서 사본)
- 게시 툴: Buffer 무료 플랜 (채널 3개, 채널당 대기열 10개). 인스타 첫 댓글 자동화는 Essentials 유료에서만. 틱톡 고정댓글은 어떤 플랜도 불가, 수동.

## 4. Batch 1 슬롯 (사이트 자동 공개일은 미국 날짜, START=2026-09-16, 슬롯 N은 START+(N-1)일)
| 슬롯 | 공개일 | 파일 | 제품 | ASIN |
|---|---|---|---|---|
| 1 | 09-16 | 2026-09-09_@jess.favoritefinds_7683380807334956318.mp4 | Mellow MarshMellow Comforter, pick your color | B0GQWK2D7L |
| 2 | 09-17 | 2026-02-06_@jess.favoritefinds_7603475581237251359.mp4 | Mellow MarshMellow Comforter, White | B0GQWK2D7L |
| 3 | 09-18 | 2026-09-02_@mrs.nikialexa_7680933683120835862.mp4 | SCOUPS Soft Top Silicone Ladle | B0CKGXMBFR |
| 4 | 09-19 | 2026-03-12_@myaquasplash_7616067171260632333.mp4 | Mellow MarshMellow Comforter, Baby Pink | B0GQWK2D7L |
| 5 | 09-20 | 2025-11-06_@electro.galaxy.shop_7569279437561203988.mp4 | Flat LED Book Light | B0F59B1YD8 |
| 6 | 09-21 | 2026-05-24_@hannahbentley_7643229668631383309.mp4 | Mellow MarshMellow Comforter, Baby Blue | B0GQWK2D7L |
| 7 | 09-22 | 2026-04-21_@morrowmoon0_7630867654085053727.mp4 | Pop Up Floss Pick Case, 2 pack | B0H44LLZLY |
| 8 | 09-23 | 2026-02-07_@hannahbentley_7603860160955632909.mp4 | Mellow MarshMellow Comforter, Sand | B0GZLX82G9 |
| 9 | 09-24 | 2026-09-01_@megansue100_7680346025726463245.mp4 | Mellow MarshMellow Comforter, Espresso | B0GQWK2D7L |

슬롯 1은 Buffer에서 2026-09-16 22:05 KST(= 09:05 ET) 게시 예정. ASIN은 Mochi가 전부 검수 완료.
전체 캡션/고정댓글/사이트 문구는 batch1_copy.md에 있음.

## 5. 사이트 구조와 재생성 방법
- 단일 파일 index.html. 썸네일(영상 프레임 캡처)과 프로필 사진은 data URI로 내장. 제품마다 date가 있고 뷰어의 오늘 날짜 이후인 것만 표시, 최신 1개는 상단 큰 카드 "New today", 나머지는 2열 그리드. Shop/Links 탭. 하단 아마존 고지문. 라이트/다크 모드.
- 디자인 기준: 럭셔리하고 차분하고 clean. 아이보리 배경, Cormorant Garamond 세리프 제목 + Inter 본문, 검정 필 버튼. 벤치마크는 linktr.ee/leila_daily_finds.
- 저장소에 있는 것: index.html(사이트), build_batch2.py, build_site2.py, catalog.json, thumbs/01.jpg~09.jpg(사이트에 박힌 썸네일과 동일한 바이트), profile.jpg, batch1_copy.md, 이 문서.
- 영상 없이 재생성 (날짜나 IG 핸들만 바꿀 때): 저장소 루트에서 `python3 build_site2.py`만 실행하면 catalog.json + thumbs/ + profile.jpg로 index.html을 다시 만든다. 표준 라이브러리만 필요. 현재 index.html은 이 방식으로 재생성해도 바이트 단위로 동일함(2026-09-16 확인). START 날짜와 IG 핸들은 build_site2.py 상단 변수.
- 영상부터 재생성 (새 배치): 영상 파일들이 있는 폴더에서 `python3 build_batch2.py` (ffmpeg, Pillow 필요. out/에 catalog_embedded.json, catalog.json, batch1_copy.md, thumbs/ 생성) → out/ 폴더에서 `python3 build_site2.py` (profile.jpg 필요) → index.html. catalog_embedded.json이 있으면 그걸 우선 읽는다.
- 새 배치 추가 시: build_batch2.py의 items 리스트에 항목 추가(파일명, 크리에이터, 썸네일 시각 t, ASIN, name/short/sub/cap/pin/tags), publish_day 이어서 번호 매김. 생성된 catalog.json과 out/thumbs/를 저장소에 함께 올려야 다음 세션이 영상 없이 재생성할 수 있다.
- 캡션의 "look for" 이름(short)은 사이트 카드 제목(name)과 맞춰 둔다. 슬롯 5는 "Flat LED Book Light"로 통일함. 슬롯 1은 이미 게시된 캡션이 "MarshMellow Comforter (10 colors)"인데 사이트 제목 "Mellow MarshMellow Comforter, pick your color"로도 찾을 수 있어 그대로 둠.

## 6. 환경 제약 (확인된 것)
- 드라이브 커넥터로 영상 다운로드는 약 5MB 이하만 안정적. 그 이상은 채팅 첨부로 받음.
- 아마존 상품 페이지 직접 fetch 불가(robots). ASIN은 웹 검색 결과로 확정하고 사람이 검수. 가격/별점 자동 수집 불가. PA-API는 판매 3건 이후 신청 가능.
- 인스타/틱톡 페이지 fetch 불가. Whisper 등 음성인식 모델 다운로드 차단(말하는 영상은 전사 API 필요).
- GitHub push는 저장소를 소스로 선택한 세션에서만 가능. 드라이브 커넥터는 파일 생성만 가능, 기존 파일 내용 수정과 공개 공유 설정은 불가.
- 소스 연결 세션에서도 sarahspick.github.io 자체는 fetch가 막혀 있음(egress 차단). 배포 확인은 GitHub Actions의 Pages 빌드 결과로 한다. 사이트 실제 화면 확인은 Mochi가 브라우저로.
- 소스 연결 세션에는 Pillow와 ffmpeg가 없음. build_batch2.py(영상 → 썸네일)는 로컬이나 다른 환경에서 돌리고, build_site2.py는 소스 연결 세션에서 돌릴 수 있다.

## 7. 파이프라인 (확정된 순서)
0. Mochi: 허락받은 최종 편집본을 드라이브 작업 폴더에 넣는다 (파일명 안 바꿔도 됨).
1. Claude: 전부 받아서 프레임 분석 → 제품 식별 → ASIN 검색 → 순서 결정(강한 훅과 30달러 이하 제품 앞에, 같은 카테고리 연속 금지, 시즌 제품은 시기 맞춤) → 검수표(구글시트) + 문구 + 썸네일 생성.
2. Mochi: 검수표에서 ASIN O/X.
3. Claude: index.html 재생성 후 저장소에 push (소스 연결된 세션) 또는 파일 전달.
4. Mochi: Buffer에 영상 + 캡션 예약 (한국 아침 8시 = 미국 동부 저녁 7시. 이번 첫 게시만 밤 10시 5분). 고정댓글은 게시 후 수동.
5. 주 1회 어소시에이트 리포트 확인 → 다음 촬영/소싱 리스트에 반영.

## 8. 진행 상황 (2026-09-16 밤)
- 완료: 새 index.html이 main에 올라가고 Pages 배포 성공(커밋 3e77399, 22:24 KST). 9개 슬롯 날짜 09-16~09-24, 링크 태그 hp302-20, IG 링크 @sarahspick 확인. 날짜 필터 로직도 검증함(09-15 이전은 빈 화면, 09-16은 슬롯 1만, 이후 매일 1개씩 추가, 최신이 상단 큰 카드).
- 완료: 소스 연결 세션 전환(이 세션). 저장소만으로 사이트 재생성 가능하게 정리(thumbs/ 추가, build_site2.py 수정).
- 완료: 슬롯 5 캡션의 "look for" 이름을 사이트 제목과 통일(batch1_copy.md, build_batch2.py).

## 9. 다음 할 일
- Mochi 오늘: Buffer에 슬롯 2~9 예약(슬롯 5는 수정된 batch1_copy.md 캡션 사용), 사이트 주소 https://sarahspick.github.io 어소시에이트 등록, 브라우저로 사이트 열어 슬롯 1 카드가 보이는지 확인.
- 첫 게시 후: 게시물 캡션의 "look for" 이름과 사이트 카드가 맞물리는지, 고정댓글 링크가 열리는지 확인.
- 본게임(100개) 전: 5MB 초과 영상 전달 방식 결정(드라이브 다운로드 한계), 인스타 핸들 확정(다르면 build_site2.py의 IG 변수 수정 후 `python3 build_site2.py`로 재생성해서 push), 인스타 첫 댓글 자동화 필요하면 Buffer Essentials 검토.
