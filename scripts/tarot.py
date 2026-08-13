#!/usr/bin/env python3
"""
타로 카드 드로우 (78장 라이더-웨이트-스미스 표준 덱, 메이저 22장 + 마이너 56장).

고정된 78장 카드 목록과 그때그때의
랜덤 드로우 결과(카드 ID·이름·정/역방향·포지션 라벨)만 출력한다. 카드 의미 해석은
이 스크립트가 아니라 Claude가 이미 갖고 있는 타로 지식으로 직접 풀어낸다
(CLAUDE.md의 "타로 드로우" 섹션 참고).

사용법:
    # 1) 전체 78장 덱을 ID와 함께 확인 (참고/검증용)
    python3 scripts/tarot.py list

    # 2) 카드 한 장 뽑기 (기본: 1장, --spread single과 동일)
    python3 scripts/tarot.py draw

    # 3) 프리셋 스프레드로 뽑기
    python3 scripts/tarot.py draw --spread three          # 과거-현재-미래 3장
    python3 scripts/tarot.py draw --spread celtic-cross   # 켈틱 크로스 10장

    # 4) 프리셋 없이 자유 매수 뽑기 (예: 5장)
    python3 scripts/tarot.py draw --count 5

역방향:
    뽑힌 카드마다 50/50 확률로 정방향/역방향을 독립적으로 굴린다 — 비율을 조정하는
    옵션은 두지 않는다 (표준 타로 관례).
"""

import argparse
import random

MAJOR_ARCANA = [
    "The Fool",
    "The Magician",
    "The High Priestess",
    "The Empress",
    "The Emperor",
    "The Hierophant",
    "The Lovers",
    "The Chariot",
    "Strength",
    "The Hermit",
    "Wheel of Fortune",
    "Justice",
    "The Hanged Man",
    "Death",
    "Temperance",
    "The Devil",
    "The Tower",
    "The Star",
    "The Moon",
    "The Sun",
    "Judgement",
    "The World",
]

SUITS = ["Wands", "Cups", "Swords", "Pentacles"]

RANKS = [
    "Ace",
    "Two",
    "Three",
    "Four",
    "Five",
    "Six",
    "Seven",
    "Eight",
    "Nine",
    "Ten",
    "Page",
    "Knight",
    "Queen",
    "King",
]

# ID 체계: 메이저는 자기 인덱스(0-21), 마이너는 22 + suit_index*14 + rank_index (22-77).
# CARD_NAMES가 이 순서로 두 목록을 이어붙인 유일한 소스 오브 트루스 — list/draw 둘 다
# 여기서만 이름을 가져오므로 서로 어긋날 일이 없다.
CARD_NAMES = MAJOR_ARCANA + [f"{rank} of {suit}" for suit in SUITS for rank in RANKS]
assert len(CARD_NAMES) == 78

SPREADS = {
    "single": ["카드"],
    "three": ["과거", "현재", "미래"],
    "celtic-cross": [
        "1. 현재 상황",
        "2. 장애물",
        "3. 근본 원인 / 무의식",
        "4. 과거",
        "5. 목표 / 의식적 바람",
        "6. 가까운 미래",
        "7. 자기 자신의 태도",
        "8. 외부 환경",
        "9. 희망과 두려움",
        "10. 최종 결과",
    ],
}


def draw_cards(n):
    """n장을 중복 없이 뽑고 각각 역방향 여부를 독립적으로 판정한다."""
    ids = random.sample(range(78), n)
    return [(card_id, random.random() < 0.5) for card_id in ids]  # (id, is_reversed)


def position_labels(spread, count):
    if spread:
        return SPREADS[spread]
    if count == 1:
        return SPREADS["single"]
    return [f"{i}번째 카드" for i in range(1, count + 1)]


def cmd_list(args):
    print("# Tarot deck (78장, ID 0-77)\n")
    print("## Major Arcana (0-21)")
    for i, name in enumerate(MAJOR_ARCANA):
        print(f"{i:2d}  {name}")
    print()
    for s_i, suit in enumerate(SUITS):
        lo = 22 + s_i * 14
        hi = lo + 13
        print(f"## Minor Arcana — {suit} ({lo}-{hi})")
        for r_i, rank in enumerate(RANKS):
            print(f"{lo + r_i:2d}  {rank} of {suit}")
        print()


def cmd_draw(args):
    if args.count is not None and args.count < 1:
        raise SystemExit("--count must be >= 1")

    if args.spread:
        labels = SPREADS[args.spread]
        header = f"# Tarot draw — {args.spread}"
    else:
        count = args.count if args.count else 1
        labels = position_labels(None, count)
        header = f"# Tarot draw — {len(labels)}장"

    if len(labels) > 78:
        raise SystemExit("한 벌(78장)보다 많이 뽑을 수 없다")

    drawn = draw_cards(len(labels))

    print(header + "\n")
    for label, (card_id, is_reversed) in zip(labels, drawn):
        name = CARD_NAMES[card_id]
        orientation = "역방향" if is_reversed else "정방향"
        print(f"{label:14s}{name:24s}{orientation}")


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="전체 78장 덱을 ID와 함께 출력 (참고용)")
    p_list.set_defaults(func=cmd_list)

    p_draw = sub.add_parser("draw", help="카드를 실제로 랜덤 드로우")
    group = p_draw.add_mutually_exclusive_group()
    group.add_argument(
        "--spread",
        choices=["single", "three", "celtic-cross"],
        help="프리셋 스프레드 선택",
    )
    group.add_argument(
        "--count", type=int, help="자유 매수 드로우 (스프레드 미사용 시, 기본 1장)"
    )
    p_draw.set_defaults(func=cmd_draw)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
