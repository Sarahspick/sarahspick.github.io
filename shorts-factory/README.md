# 야생CCTV 쇼츠 공장

세렝게티 무인카메라 실제 사진으로 한국어 스토리 쇼츠를 자동 제작하는 파이프라인입니다.
명령 한 줄이면 30편이 `다운로드/야생CCTV` 폴더에 만들어집니다.

## 문서

1. [`docs/01_레퍼런스_채널_분석.md`](docs/01_레퍼런스_채널_분석.md): 겜토리(@겜토뤼) 287개 쇼츠 분석, 소스·편집·제목 공식
2. [`docs/02_채널_기획.md`](docs/02_채널_기획.md): 채널명, 컨셉, 포맷, 업로드 운영, 수익화 현실
3. [`docs/03_자동화_설계.md`](docs/03_자동화_설계.md): 자동화 구조, CapCut 대신 코드 편집을 택한 이유, 완전 자동화 로드맵

## 내 컴퓨터에서 30편 만들기 (Windows / Mac)

1. Python 3.10 이상 설치 (Windows는 설치 화면에서 "Add Python to PATH" 체크)
2. 이 폴더에서 터미널(명령 프롬프트)을 열고:

```bash
pip install -r requirements.txt
python make_shorts.py render
```

3. 끝나면 `다운로드/야생CCTV` 폴더에 MP4 30개와 `업로드_정보.csv`, `업로드_정보.md`(제목·설명·고정 댓글)가 생깁니다.

ffmpeg는 `imageio-ffmpeg` 패키지에 포함되어 있어 따로 설치할 필요가 없습니다. 사진은 처음 한 번만 Google Cloud 공개 저장소에서 받아 `~/.cache/yasaeng-cctv`에 저장합니다.

자주 쓰는 옵션:

```bash
python make_shorts.py render --only 1,5,7       # 특정 편만
python make_shorts.py render --out D:/쇼츠       # 저장 위치 변경
python make_shorts.py preview 7                 # 7편 장면별 미리보기 이미지 (검수용)
python make_shorts.py meta                      # 업로드 정보만 다시 생성
```

## 새 편 만들기

1. 소재 찾기 (메타데이터 약 370MB를 처음 한 번 내려받습니다):

```bash
python make_shorts.py mine rare                  # 희귀종 후보 + 접촉 인화지(contact sheet)
python make_shorts.py mine events                # 초식동물 → 몇 분 뒤 포식자 등장
python make_shorts.py mine closeups leopard      # 렌즈 코앞 근접 사진
python make_shorts.py mine site S5 P03       # 카메라 한 대에 찍힌 모든 종
python make_shorts.py mine fire                  # 초원 화재
```

결과는 `mining/` 폴더에 이미지(10% 격자 포함)와 텍스트 목록으로 저장됩니다.

2. `stories/catalog.py`에 이야기 한 편을 추가합니다. 한 편은 "비트(beat)" 목록이고, 비트 하나가 화면 하나입니다.

```python
dict(slug="black_rhino", title=["0.003% 확률로 찍힌", "{검은코뿔소}"], mood="mystery",
     yt_title="...", desc="...", tags=["코뿔소"], animal="검은코뿔소", pin="...",
     beats=[
         dict(shot=S("SER_S2#F12#1#124"), cam="punch", text="새벽 2시 37분, 카메라 앞에 {뿔 두 개}",
              fx=["shake"], sfx=["impact"]),
         card("266만 번 중 {71번}", "세렝게티 무인카메라에 코뿔소가 찍힌 횟수"),
         ...
     ])
```

| 키 | 의미 |
|---|---|
| `S(촬영ID, 사용할_프레임, 초점박스)` | 촬영 한 건. 초점박스는 [x0, y0, x1, y1] (0~1 비율, 격자로 읽기) |
| `cam` | drift(천천히) · push(줌인) · pull(줌아웃) · punch(순간 확대) · hold · pan_lr · pan_rl · fit(전체) |
| `text` | 자막. `{중괄호}` 부분이 노란색 강조 |
| `trans` | 들어오는 전환: cut · static(지지직) · flash · fade · rewind(되감기) · whoosh |
| `fx` | shake(흔들림) · flash · circle(빨간 원) · freeze(정지화면 느낌) |
| `sfx` | impact · riser · ding · pop · whoosh · scratch · heartbeat:초 · fire:초 (`이름@0.5`는 0.5초 뒤) |
| `callout` | 동물 이름표 `call("표범", at=0.4)` |
| `card(...)` | 숫자·팩트 카드 화면 |
| `mood` | 배경음악: suspense · mystery · cute · epic · sad · funny |

3. `python make_shorts.py build`로 JSON을 만들고, `preview`로 확인한 뒤 `render` 하면 끝입니다.

## 구조

```
make_shorts.py        명령줄 도구 (build / render / preview / meta / mine)
factory/lila.py       Snapshot Serengeti 데이터 접근 (이미지 캐시, 메타데이터 인덱스)
factory/engine.py     렌더러: 레이아웃, 자동 줌, HUD, 자막, 전환, 효과 → ffmpeg
factory/audio.py      효과음·배경음악·주변음 합성, 믹싱 (-14 LUFS 정규화)
factory/text.py       한글 자막 렌더링 (강조, 줄바꿈 규칙)
factory/mine.py       소재 발굴 (희귀종, 사건, 근접, 한 자리 몽타주, 화재)
stories/catalog.py    30편 대본
stories/json/         렌더용 스토리 파일 (사진 경로·초점 포함, 메타데이터 없이 렌더 가능)
assets/fonts/         한글 폰트 (모두 SIL Open Font License)
```

## 출처와 라이선스

1. 사진: Snapshot Serengeti (Swanson et al. 2015, *Scientific Data* 2:150026), LILA BC 공개 데이터셋, Community Data License Agreement Permissive 1.0. 상업적 이용과 수정 허용. 모든 영상 하단과 설명란에 출처를 표기합니다.
2. 폰트: Black Han Sans, Gothic A1, VT323, Share Tech Mono (SIL Open Font License 1.1, 라이선스 파일 동봉).
3. 음악·효과음: `factory/audio.py`가 매번 새로 합성하는 자체 제작 사운드.
