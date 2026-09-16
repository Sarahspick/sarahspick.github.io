# Sarah's Pick 인수인계 문서 (2026-09-16 밤, 5차 갱신)

이 문서는 Claude가 다음 세션에서 그대로 이어서 일할 수 있도록 쓴 것. 사람(Mochi)과 Claude 둘 다 읽는 용도.

## 1. 사업 한 줄 요약
미국 타겟 인스타그램 계정 Sarah's Pick에 제품 숏폼을 하루 1개 올리고, bio 사이트(sarahspick.github.io)에서 아마존 제휴 링크로 연결해 수익을 내는 사업. 목표는 최대한 자동화.

## 2. 절대 규칙
- 영상은 직접 촬영했거나 원작자 허락을 받은 것만 쓴다. 무단 재업로드, 텍스트만 덮는 편집, 다운로드 툴 우회는 하지 않는다. Batch 1의 9개는 모두 허락받은 최종 편집본이라고 Mochi가 확인함. 편집은 Claude가 하지 않는다.
- 문구 규칙 (Mochi 지시): 대시 기호("—", "-") 절대 금지. 모든 문장은 20대 여성이 쓴 듯 짧고 감성적으로, 한 문장 또는 최대 두 문장, 이모지 적극 사용, 사람 느낌. 채팅 답변에도 대시 금지.
- 고정댓글 맨 끝에는 반드시 "As an Amazon Associate I earn from qualifying purchases." (아마존 약관). 캡션 해시태그에 #affiliate 포함 (FTC).
- 제휴 링크 형식: https://www.amazon.com/dp/ASIN?tag=hp302-20 (SiteStripe 불필요, 제3자 단축링크 금지). Mochi가 SiteStripe에서 만든 amzn.to 링크는 아마존 공식 단축이라 그대로 써도 됨.
- 사이트 중복 규칙 (Mochi 지시, 2026-09-16): 영상은 같은 제품이 여러 개여도 되지만, 사이트에는 제품당 카드 하나만. catalog의 product 키(없으면 ASIN)가 같으면 한 카드로 합쳐지고, 첫 영상의 제목/썸네일/링크가 대표가 되며, 그 제품의 새 영상이 올라가는 순간 카드가 맨 위 "New today"로 다시 올라온다. Batch 1의 이불 6개(슬롯 1, 2, 4, 6, 8, 9)는 product=marshmellow-comforter로 묶여 슬롯 1 카드(pick your color, 링크 B0GQWK2D7L) 하나로 보임. 슬롯 8 Sand는 ASIN이 B0GZLX82G9로 다른데도 같은 이불로 묶었음. 별도 상품이면 product를 ASIN으로 되돌리면 카드가 분리됨.

## 3. 계정과 자산
- 아마존 어소시에이트 태그: hp302-20. 인스타 주소와 사이트 주소(https://sarahspick.github.io) 둘 다 등록 완료.
- 인스타그램: Sarah's Pick, 비즈니스 계정으로 전환 중. 핸들 가정값 @sarahspick (사이트에 이 링크가 박혀 있음. 실제 핸들이 다르면 build_site2.py의 IG 변수 수정).
- GitHub: 사용자 Sarahspick, 저장소 Sarahspick/sarahspick.github.io (공개, main 브랜치, 루트의 index.html이 사이트). 저장소를 세션 소스로 선택한 세션만 push 가능 (2026-09-16 소스 연결 세션에서 push 확인됨). main에 올리면 GitHub Pages가 1분 안에 자동 배포함 (Actions 탭의 "pages build and deployment"가 success면 반영 완료).
- 구글 드라이브 (hw54974875@gmail.com 계정, Claude 드라이브 커넥터 연결됨):
  - 작업 폴더 ID 1cJSARFOFkpssp5s4RfenM2eSp0dzPAtz (영상 9개 원본)
  - 출력 폴더 01_batch1_output ID 1_gF8h-GJMAJ5Yf2NXtG7AnNbcvtXmr9A (검수표 구글시트, 문구, 이 문서 사본)
- 게시 툴: Buffer 무료 플랜 (채널 3개, 채널당 대기열 10개). 인스타 첫 댓글 자동화는 Essentials 유료에서만. 틱톡 고정댓글은 어떤 플랜도 불가, 수동.

## 4. Batch 1 슬롯
### 실제 게시 일정 (Mochi 확정, 2026-09-16 밤. catalog.json의 publish_day가 기준, null이면 정지)
| 날짜 (KST 09:00) | publish_day | 제품 | 슬롯 파일 |
|---|---|---|---|
| 09-16 (22:05 게시됨) | 1 | Mellow MarshMellow Comforter, pick your color | 슬롯 1 |
| 09-17 | 2 | SCOUPS Soft Top Silicone Ladle | 슬롯 3 |
| 09-18 | 3 | Flat LED Book Light | 슬롯 5 |
| 09-19 | 4 | Pop Up Floss Pick Case, 2 pack | 슬롯 7 |
| 09-20 이후 | 정지 | 이불 영상 5개(슬롯 2, 4, 6, 8, 9)는 보류. 다시 쓰려면 catalog.json에서 해당 항목 publish_day에 번호를 넣고 재생성 | |

프로젝터(슬롯 0, publish_day 0)는 이미 게시된 영상이라 사이트에 처음부터 보임.

### 원래 슬롯 표 (파일과 ASIN 참조용, 날짜는 위 표가 우선)
| 슬롯 | 공개 (KST 09:00) | 파일 | 제품 (사이트 제목) | ASIN |
|---|---|---|---|---|
| 1 | 09-16 (실제 22:05 게시됨) | 2026-09-09_@jess.favoritefinds_7683380807334956318.mp4 | Mellow MarshMellow Comforter, pick your color ☁️🌈 | B0GQWK2D7L |
| 2 | 09-17 | 2026-02-06_@jess.favoritefinds_7603475581237251359.mp4 | Mellow MarshMellow Comforter, White ☁️🤍 | B0GQWK2D7L |
| 3 | 09-18 | 2026-09-02_@mrs.nikialexa_7680933683120835862.mp4 | SCOUPS Soft Top Silicone Ladle 🍝 | B0CKGXMBFR |
| 4 | 09-19 | 2026-03-12_@myaquasplash_7616067171260632333.mp4 | Mellow MarshMellow Comforter, Baby Pink 🎀 | B0GQWK2D7L |
| 5 | 09-20 | 2025-11-06_@electro.galaxy.shop_7569279437561203988.mp4 | Flat LED Book Light 📖✨ | B0F59B1YD8 |
| 6 | 09-21 | 2026-05-24_@hannahbentley_7643229668631383309.mp4 | Mellow MarshMellow Comforter, Baby Blue 🩵☁️ | B0GQWK2D7L |
| 7 | 09-22 | 2026-04-21_@morrowmoon0_7630867654085053727.mp4 | Pop Up Floss Pick Case, 2 pack 🦷💗 | B0H44LLZLY |
| 8 | 09-23 | 2026-02-07_@hannahbentley_7603860160955632909.mp4 | Mellow MarshMellow Comforter, Sand 🤎 | B0GZLX82G9 |
| 9 | 09-24 | 2026-09-01_@megansue100_7680346025726463245.mp4 | Mellow MarshMellow Comforter, Espresso ☕🤍 | B0GQWK2D7L |

- 게시 시각 규칙 (Mochi 결정, 2026-09-16): 인스타 릴스는 매일 한국시각 오전 9시. 미국 동부로는 전날 저녁 8시(11월 1일 서머타임 종료 후엔 저녁 7시). 사이트도 같은 순간(UTC 00:00)에 해당 슬롯을 공개하므로 어느 나라에서 보든 릴스와 사이트가 동시에 열린다.
- 슬롯 1은 22:05 KST에 이미 게시됨. 사이트에선 이미 보이는 상태라 문제 없음.
- ASIN은 Mochi가 전부 검수 완료. 사이트 카드는 제목(이모지 포함)만 보여주고 설명 문장은 없음.
- 슬롯 0 (배치 밖, 이미 게시된 영상): Book Beam Projector 📽️✨, 링크 https://amzn.to/4heL25Z (ASIN 미확인, 이 환경에서 아마존 접속 불가), product=book-beam-projector, 사이트에는 09-15부터 보이는 것으로 설정. 썸네일 thumbs/00.jpg는 임시 이미지(아이보리 배경에 📽️). Mochi가 제품 사진을 드라이브 01_batch1_output 폴더에 올리면 Claude가 4:5로 잘라 교체. 앞으로 프로젝터 영상을 또 올려도 카드는 하나로 유지되며 위로 올라옴.
전체 캡션/고정댓글/사이트 문구는 batch1_copy.md에 있음.

## 5. 사이트 구조와 재생성 방법
- 단일 파일 index.html. 썸네일과 프로필 사진은 data URI로 내장. 제품마다 live_at(UTC 시각)이 있고 지금 시각을 지난 것만 표시, 최신 1개는 상단 큰 카드 "New today", 나머지는 2열 그리드. 탭 없음(Links 탭은 인스타 링크 하나뿐이라 제거, 인스타는 헤더 pill). 헤더 아래 검색창: 제품명 + catalog의 keywords(브랜드, 긴 이름, 색상) + 카테고리를 단어 단위로 즉시 필터, 검색 중엔 큰 카드 없이 2열 그리드만. 하단 아마존 고지문.
- 제품명은 릴스 캡션의 "look for" 이름과 바로 이어지도록 제품답게 풀네임으로(예: "SCOUPS Soft Top Silicone Ladle 🍝"). Mochi가 미니멀 제품명은 취소함(2026-09-16). 색상 등 추가 검색어는 keywords에.
- 썸네일: 기본은 thumbs/NN.jpg(릴스 프레임). catalog 항목에 "thumb": "경로"를 넣으면 그 파일(아마존 공식 제품 사진 등)을 대신 쓴다. Mochi가 릴스 프레임은 화질이 낮고 덜 전문적이라 판단, 공식 제품 사진으로 교체 예정(벤치마크 linktr.ee/roastingAF). 사진은 4:5(480x600)로 잘라 넣는다.
- 디자인 기준 (2026-09-16 4차): PC(640px 이상)에서는 가운데 모바일 폭 영역만 진한 아이보리의 둥근 패널(32px 라운드, 옅은 그림자)이고 바깥 페이지는 밝은 아이보리(#f4efe7). 폰에서는 화면 전체가 진한 아이보리. 럭셔리하고 차분하고 clean. 항상 살짝 진한 웜 아이보리 배경(#ece4d8, 위쪽 그라데이션 #e4dbcd, 카드 #faf7f2, 다크 모드 없음), 폰트는 Plus Jakarta Sans 하나로 통일(세리프 없음, Mochi가 세리프를 구식이라 함), 검정 필 버튼. 카드에는 제목 + 이모지만, 설명 문장 없음. 큰 카드와 그리드 사이에 "All my picks" 대신 감성 문구 한 줄("treat yourself to something lovely today 🤍"). 벤치마크는 linktr.ee/leila_daily_finds.
- 저장소에 있는 것: index.html(사이트), build_batch2.py, build_site2.py, catalog.json, thumbs/01.jpg~09.jpg(사이트에 박힌 썸네일과 동일한 바이트), profile.jpg, batch1_copy.md, 이 문서.
- 영상 없이 재생성 (날짜나 IG 핸들만 바꿀 때): 저장소 루트에서 `python3 build_site2.py`만 실행하면 catalog.json + thumbs/ + profile.jpg로 index.html을 다시 만든다. 표준 라이브러리만 필요. 게시 시작일(START_KST), 매일 게시 시각(POST_KST), IG 핸들은 build_site2.py 상단 변수.
- 영상부터 재생성 (새 배치): 영상 파일들이 있는 폴더에서 `python3 build_batch2.py` (ffmpeg, Pillow 필요. out/에 catalog_embedded.json, catalog.json, batch1_copy.md, thumbs/ 생성) → out/ 폴더에서 `python3 build_site2.py` (profile.jpg 필요) → index.html. catalog_embedded.json이 있으면 그걸 우선 읽는다.
- 새 배치 추가 시: build_batch2.py의 items 리스트에 항목 추가(파일명, 크리에이터, 썸네일 시각 t, ASIN, name(이모지 포함)/short/cap/pin/tags, 같은 제품이면 product 키로 묶기), publish_day 이어서 번호 매김. 사이트 중복은 자동으로 합쳐지므로 같은 제품 영상을 여러 개 넣어도 카드는 하나. 생성된 catalog.json과 out/thumbs/를 저장소에 함께 올려야 다음 세션이 영상 없이 재생성할 수 있다.
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
4. Mochi: Buffer에 영상 + 캡션 예약 (매일 한국시각 오전 9시. 첫 게시만 22:05였음). 고정댓글은 게시 후 인스타 앱에서 수동. 방법은 10번 참고.
5. 주 1회 어소시에이트 리포트 확인 → 다음 촬영/소싱 리스트에 반영.

## 8. 진행 상황 (2026-09-16 밤)
- 완료: 새 index.html이 main에 올라가고 Pages 배포 성공(커밋 3e77399, 22:24 KST). 9개 슬롯 날짜 09-16~09-24, 링크 태그 hp302-20, IG 링크 @sarahspick 확인. 날짜 필터 로직도 검증함(09-15 이전은 빈 화면, 09-16은 슬롯 1만, 이후 매일 1개씩 추가, 최신이 상단 큰 카드).
- 완료: 소스 연결 세션 전환(이 세션). 저장소만으로 사이트 재생성 가능하게 정리(thumbs/ 추가, build_site2.py 수정).
- 완료: 슬롯 5 캡션의 "look for" 이름을 사이트 제목과 통일(batch1_copy.md, build_batch2.py).
- 완료 (2차): 배경을 더 밝은 아이보리로, 다크 모드 제거, 카드 설명 문장 제거하고 제목에 이모지, 공개 시각을 한국 오전 9시 기준 정확한 시각(live_at)으로 변경. 어소시에이트에 사이트 주소 등록 완료(Mochi).
- 완료: PR #1 합쳐짐(Mochi, 22:49 KST). bio 링크 등록 완료. Buffer 예약 완료(Mochi).
- 완료 (3차): 사이트 제품 중복 제거(제품당 카드 하나), Book Beam Projector 카드 추가(사진은 임시), 디자인 재조정(진한 아이보리, Plus Jakarta Sans, 감성 문구).
- 완료 (4차): Links 탭 제거, 검색 UI, PC용 가운데 패널 레이아웃, 검색 키워드, thumb 경로 지원.
- 완료 (5차): 제품명 풀네임으로 복구, 게시 일정을 16 이불 / 17 국자 / 18 북라이트 / 19 치실 케이스 / 20일부터 정지로 변경(publish_day null = 정지).

## 9. 다음 할 일
- 제품 사진 5장(프로젝터, 이불, 국자, 북라이트, 치실 케이스)을 Mochi가 드라이브 01_batch1_output 안에 photos 폴더를 만들어 업로드. 파일명은 제품 이름으로(projector.jpg, comforter.jpg, ladle.jpg, booklight.jpg, floss.jpg). 5MB 이하 jpg/png. Claude가 받아서 4:5로 잘라 thumbs/에 넣고 catalog의 thumb 경로를 채운 뒤 재생성. 채팅에 붙인 이미지는 Claude가 파일로 꺼낼 수 없고, 이 환경은 아마존/브랜드 사이트 접속이 막혀 있어 직접 못 가져온다.
- 프로젝터 ASIN 확인해서 링크를 표준 형식으로 바꾸기 (선택).
- 새 PR을 main에 합치기.
- 첫 게시 후: 게시물 캡션의 "look for" 이름과 사이트 카드가 맞물리는지, 고정댓글 링크가 열리는지 확인.
- 본게임(100개) 전: 5MB 초과 영상 전달 방식 결정(드라이브 다운로드 한계), 인스타 핸들 확정(다르면 build_site2.py의 IG 변수 수정 후 `python3 build_site2.py`로 재생성해서 push), 인스타 첫 댓글 자동화 필요하면 Buffer Essentials 검토.

## 10. Buffer 예약 방법 (Mochi가 직접. Claude는 Mochi의 Buffer/인스타 로그인과 영상 파일에 접근할 수 없고, Buffer는 외부 자동화용 API도 닫혀 있어서 대신 못 함)
1. buffer.com 무료 가입 → Channels → Connect → Instagram. 페이스북 로그인으로 Sarah's Pick 비즈니스(또는 크리에이터) 계정을 연결한다.
2. 채널 Settings → Posting Schedule: 시간대를 Asia/Seoul로, 매일 09:00 시간 하나만 남긴다.
3. Create Post → 인스타 채널 선택 → 영상 업로드 → 형식 Reel → batch1_copy.md의 "인스타 캡션" 블록을 그대로 붙여넣기 → Add to Queue (자동으로 다음 09:00 슬롯에 들어감). 날짜를 직접 정하고 싶으면 Schedule Post에서 09-17 09:00, 09-18 09:00... 순서대로.
4. 무료 플랜은 채널당 대기열 10개. 슬롯 2~9는 8개라 한 번에 다 들어간다.
5. 게시된 다음 인스타 앱에서 릴스 열기 → "고정 댓글" 블록을 댓글로 달기 → 내 댓글을 길게 눌러 고정(Pin). 마지막 줄 "As an Amazon Associate..."는 꼭 포함.
6. 대안: 인스타 앱 자체 예약(전문가 계정에서 릴스 올릴 때 고급 설정 → 예약)도 무료이고 75일 앞까지 가능. Buffer가 번거로우면 이걸로 해도 결과는 같다.
7. 나중에 100개 본게임에서 자동화하려면 Meta 개발자 앱 + Instagram Graph API로 공개 URL의 영상을 릴스로 올리는 스크립트가 가능하다(비즈니스 계정 + 페이스북 페이지 연결 필요). 그때 Claude가 스크립트를 만들면 됨.
