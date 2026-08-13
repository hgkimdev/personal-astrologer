# 개인 점성술사

Claude Code 위에서 돌아가는 개인 점성술사 템플릿. 출생차트 데이터를 로컬 파일에 채워두면 그걸 근거로 질문에 답한다. 포크해서 자기 데이터로 채우면 누구나 자기만의 버전으로 쓸 수 있다.

> 오락·자기 성찰용 도구다. 전문 상담이나 의사결정을 대신하지 않는다.

## 시작하기

1. 레포를 포크하거나 클론한다.
2. `CLAUDE.md` 첫 문장의 이름을 자기 이름(또는 원하는 호칭)으로 바꾼다.
3. 아래 로컬 파일을 직접 채운다 — Claude는 이 파일들을 대신 채우거나 추측으로 수정하지 않는다(`CLAUDE.md` 가드레일 참고).

| 파일 | 내용 |
|---|---|
| `CLAUDE.local.md` | 현재 상황·성향·최근 관심사 |
| `chart.local.md` | 서양 점성술 출생차트 |

두 파일 모두 `.gitignore` 처리되어 커밋되지 않는다. 이름·생년월일시·출생지 같은 개인정보는 이 파일들 밖(커밋되는 파일)에는 절대 적지 않는다.

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
scripts/transits.py        트랜짓 계산기                 (커밋됨)
scripts/tarot.py           타로 드로우                   (커밋됨)
```

## 라이선스

MIT — [`LICENSE`](./LICENSE) 참고.
