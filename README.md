# 개인 점성술사

Claude Code 위에서 돌아가는 개인 점성술사 템플릿. 출생차트 데이터를 로컬 파일에 채워두면 그걸 근거로 질문에 답한다. 포크해서 자기 데이터로 채우면 누구나 자기만의 버전으로 쓸 수 있다.

> 오락·자기 성찰용 도구다. 전문 상담이나 의사결정을 대신하지 않는다.

## 무엇을 할 수 있나

- **서양 점성술 해석** — 품위(디그니티)·어스펙트 패턴(T-스퀘어, 스텔리움 등)·오브까지 근거로 짚어주는 서사형 리딩.
- **실시간 트랜짓/타이밍 계산** — Swiss Ephemeris 기반 실제 천문 계산으로 타이밍 질문에 감이나 일반론이 아닌 근거로 답한다.
- **타로 드로우** — 원할 때만 opt-in으로 실행되는 78장 표준 덱 드로우(싱글/3장/켈틱크로스).
- **상담일지** — 요청 시 세션을 파일로 기록하고, 여러 세션에 걸쳐 반복되는 감정/인지 패턴을 누적 추적.

## 시작하기

1. 레포를 포크하거나 클론한다.
2. `CLAUDE.md` 첫 문장의 이름을 자기 이름(또는 원하는 호칭)으로 바꾼다.
3. 아래 로컬 파일을 직접 채운다 — Claude는 이 파일들을 대신 채우거나 추측으로 수정하지 않는다(`CLAUDE.md` 가드레일 참고).

| 파일 | 내용 |
|---|---|
| `CLAUDE.local.md` | 현재 상황·성향·최근 관심사 |
| `chart.local.md` | 서양 점성술 출생차트 |

두 파일 모두 `.gitignore` 처리되어 커밋되지 않는다. 이름·생년월일시·출생지 같은 개인정보는 이 파일들 밖(커밋되는 파일)에는 절대 적지 않는다.

**`chart.local.md` 채우는 법**: 직접 계산할 필요 없이 [astro.com](https://www.astro.com)의 Free Horoscopes → Extended Chart Selection에 생년월일시·출생지를 넣으면 행성·앵글·하우스 커스프·어스펙트가 표로 나온다. 그 값을 아래 형식(별자리 D°M', 하우스)으로 옮기면 된다 — `scripts/transits.py`도 이 표기를 그대로 절대황경도로 변환해서 쓴다.

```markdown
## 3대 요소
- 태양(Sun): Aries 15°23', 1st House
- 달(Moon): Cancer 2°10', 4th House
- 상승궁(Ascendant): Aries 0°05'

## 행성 배치 (별자리 · 도수 · 하우스)
- 수성(Mercury): Pisces 28°41', 12th House
- 금성(Venus): Taurus 9°17', 2nd House
- 화성(Mars): Aries 3°02', 1st House, Retrograde
...
```

행성 배치·기타 포인트(노드·릴리스·카이런 등)·하우스 커스프·주요 어스펙트까지 전부 이 형식으로 채우면 채울수록 리딩이 정교해진다 — 처음엔 3대 요소만 채우고 시작해도 된다.

4. (선택) 트랜짓 계산기를 쓰려면 설치한다:
   ```bash
   python3 -m venv .venv && source .venv/bin/activate && pip install -r scripts/requirements.txt
   ```

## 쓰는 법

Claude Code로 레포를 열고 자연어로 물어보면 된다 — "요즘 시기가 어때?", "켈틱크로스 스프레드로 이번 달 연애운을 봐줘" 같은 식으로. 답변 톤, 가드레일은 [`CLAUDE.md`](./CLAUDE.md)에 정의돼 있다. 이름·국적 같은 캐릭터 플레이버는 `persona.md`에서 따로 조정한다.

상담 내용을 남기고 싶으면 "상담일지에 남겨줘"라고 요청하면 된다 — `journal.local/`에 세션별 파일로 기록되고, 반복되는 패턴은 `_patterns.md`에 누적된다.

## 스크립트

- `scripts/transits.py` — Swiss Ephemeris 기반 실제 트랜짓 계산. 개인정보가 없어 그대로 커밋되어 있고, 원국 데이터는 실행할 때마다 `--natal`/`--cusps` 인자로만 넘긴다.
  ```bash
  python3 scripts/transits.py positions
  python3 scripts/transits.py aspects --natal "Venus=157.03,DSC=157.23" --orb 3
  ```
- `scripts/tarot.py` — 78장 표준 덱 랜덤 드로우. 추가 설치 없이 표준 라이브러리만 사용하고, 사용자가 명시적으로 요청할 때만 쓰인다.
  ```bash
  python3 scripts/tarot.py draw --spread three
  ```

더 자세한 옵션은 각 스크립트 상단 docstring과 `CLAUDE.md`에 정리돼 있다.

## 파일 구성

```
CLAUDE.md                  페르소나·운영 지침            (커밋됨)
persona.md                 캐릭터 플레이버 (선택)         (커밋됨)
CLAUDE.local.md            현재 상황·성향                (gitignore, 직접 작성)
chart.local.md             서양 점성술 출생차트          (gitignore, 직접 작성)
journal.local/             상담 이력 (요청 시 Claude가 기록) (gitignore)
readings.local/            외부 점술 기록 (gitignore, 직접 작성)
scripts/transits.py        트랜짓 계산기                 (커밋됨)
scripts/tarot.py           타로 드로우                   (커밋됨)
```

## 라이선스

MIT — [`LICENSE`](./LICENSE) 참고.
