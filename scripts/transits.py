#!/usr/bin/env python3
"""
트랜짓 행성 위치 계산기 (Swiss Ephemeris / Moshier 알고리즘 기반).

이 스크립트는 개인정보를 전혀 포함하지 않는다 — 특정 시각의 행성 좌표(공용 천문학적
사실)만 계산한다. 출생 데이터(원국)는 이 스크립트가 아니라 chart.local.md에 있고,
아래 `aspects` 커맨드를 쓸 때 그때그때 --natal 인자로 넘겨서만 비교에 사용한다.

설치:
    python3 -m venv .venv && source .venv/bin/activate && pip install pyswisseph

사용법:
    # 1) 특정 시각의 트랜짓 행성 위치만 보기 (기본: 지금, UTC)
    python3 scripts/transits.py positions
    python3 scripts/transits.py positions --datetime "2026-07-27 09:00"

    # 2) 트랜짓 행성이 원국의 특정 지점들과 이루는 어스펙트 계산
    #    --natal "이름=절대황경도,이름=절대황경도,..."
    #    절대황경도 = 별자리 인덱스*30 + 별자리 내 도수 (Aries=0 ... Pisces=11)
    python3 scripts/transits.py aspects --natal "Venus=157.03,DSC=157.23,Saturn_natal=64.12" --orb 3

    # 3) 하우스까지 함께 보고 싶으면 --cusps 로 1~12하우스 커스프를 순서대로 전달
    python3 scripts/transits.py aspects --natal "Venus=157.03" \\
        --cusps "337.23,20.6,52.12,76.4,98.63,123.37,157.23,200.6,232.12,256.4,278.63,303.37"

시간대:
    --datetime 는 항상 UTC 기준으로 입력한다. 한국 시간(KST, UTC+9)이면 9시간을 빼서 넣을 것.
"""
import argparse
import datetime

import swisseph as swe

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Chiron(swe.CHIRON)은 seas_18.se1 에페메리스 파일이 별도로 필요해 기본 설치로는
# 계산되지 않는다 — 카이런 트랜짓이 필요하면 WebSearch로 보조 확인할 것.
PLANETS = [
    (swe.SUN, "Sun"),
    (swe.MOON, "Moon"),
    (swe.MERCURY, "Mercury"),
    (swe.VENUS, "Venus"),
    (swe.MARS, "Mars"),
    (swe.JUPITER, "Jupiter"),
    (swe.SATURN, "Saturn"),
    (swe.URANUS, "Uranus"),
    (swe.NEPTUNE, "Neptune"),
    (swe.PLUTO, "Pluto"),
    (swe.MEAN_NODE, "North Node"),
]

ASPECTS = [
    (0, "Conjunction", 8),
    (60, "Sextile", 5),
    (90, "Square", 7),
    (120, "Trine", 7),
    (180, "Opposition", 8),
]


def deg_to_sign(lon):
    lon = lon % 360
    sign_index = int(lon // 30)
    deg_in_sign = lon % 30
    d = int(deg_in_sign)
    m = round((deg_in_sign - d) * 60)
    if m == 60:
        m = 0
        d += 1
    if d == 30:
        d = 0
        sign_index = (sign_index + 1) % 12
    return f"{SIGNS[sign_index]} {d}°{m:02d}'"


def parse_datetime(s):
    if s is None:
        return datetime.datetime.now(datetime.timezone.utc)
    return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=datetime.timezone.utc)


def to_julday(dt):
    return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60)


def calc_positions(dt):
    jd = to_julday(dt)
    flag = swe.FLG_MOSEPH | swe.FLG_SPEED
    result = {}
    for code, name in PLANETS:
        (lon, lat, dist, lon_speed, lat_speed, dist_speed), _ = swe.calc_ut(jd, code, flag)
        result[name] = {"lon": lon, "speed": lon_speed}
    return result


def parse_kv_degrees(s):
    out = {}
    for pair in s.split(","):
        pair = pair.strip()
        if not pair:
            continue
        name, val = pair.split("=")
        out[name.strip()] = float(val.strip())
    return out


def which_house(lon, cusps):
    lon = lon % 360
    n = len(cusps)
    for i in range(n):
        start = cusps[i] % 360
        end = cusps[(i + 1) % n] % 360
        if start < end:
            if start <= lon < end:
                return i + 1
        else:  # wraps past 0°
            if lon >= start or lon < end:
                return i + 1
    return None


def find_aspect(transit_lon, natal_lon, orb_override):
    diff = abs((transit_lon - natal_lon + 180) % 360 - 180)
    for angle, name, default_orb in ASPECTS:
        orb = orb_override if orb_override is not None else default_orb
        delta = abs(diff - angle)
        if delta <= orb:
            return name, angle, delta
    return None


def applying_or_separating(dt, transit_code, natal_lon, aspect_angle):
    later = dt + datetime.timedelta(hours=6)
    jd_now, jd_later = to_julday(dt), to_julday(later)
    flag = swe.FLG_MOSEPH
    lon_now = swe.calc_ut(jd_now, transit_code, flag)[0][0]
    lon_later = swe.calc_ut(jd_later, transit_code, flag)[0][0]

    def orb_at(lon):
        diff = abs((lon - natal_lon + 180) % 360 - 180)
        return abs(diff - aspect_angle)

    return "applying" if orb_at(lon_later) < orb_at(lon_now) else "separating"


def cmd_positions(args):
    dt = parse_datetime(args.datetime)
    positions = calc_positions(dt)
    print(f"# Transit positions for {dt.isoformat()}\n")
    for name, data in positions.items():
        retro = " (R)" if data["speed"] < 0 else ""
        print(f"{name:12s} {data['lon']:7.3f}deg  {deg_to_sign(data['lon']):16s}{retro}")


def cmd_aspects(args):
    dt = parse_datetime(args.datetime)
    natal = parse_kv_degrees(args.natal)
    orb_override = args.orb
    cusps = None
    if args.cusps:
        cusps = [float(x) for x in args.cusps.split(",")]
        if len(cusps) != 12:
            raise SystemExit("--cusps must have exactly 12 comma-separated values (house 1..12)")

    positions = calc_positions(dt)
    code_by_name = {name: code for code, name in PLANETS}

    print(f"# Transit aspects for {dt.isoformat()}\n")
    found_any = False
    for t_name, t_data in positions.items():
        house_note = ""
        if cusps:
            h = which_house(t_data["lon"], cusps)
            house_note = f"  [natal {h}H]" if h else ""
        for n_name, n_lon in natal.items():
            hit = find_aspect(t_data["lon"], n_lon, orb_override)
            if hit:
                aspect_name, angle, delta = hit
                trend = applying_or_separating(dt, code_by_name[t_name], n_lon, angle)
                retro = " (R)" if t_data["speed"] < 0 else ""
                print(
                    f"transiting {t_name}{retro} {aspect_name} natal {n_name} "
                    f"(orb {delta:.2f}, {trend}){house_note}"
                )
                found_any = True
    if not found_any:
        print("(지정한 orb 안에서 걸리는 어스펙트 없음)")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_pos = sub.add_parser("positions", help="특정 시각의 트랜짓 행성 위치만 출력")
    p_pos.add_argument("--datetime", help="UTC 'YYYY-MM-DD HH:MM' (기본: 지금)")
    p_pos.set_defaults(func=cmd_positions)

    p_asp = sub.add_parser("aspects", help="트랜짓 행성과 원국 지점 간 어스펙트 계산")
    p_asp.add_argument("--datetime", help="UTC 'YYYY-MM-DD HH:MM' (기본: 지금)")
    p_asp.add_argument("--natal", required=True, help="'이름=절대황경도,...' 형식")
    p_asp.add_argument("--orb", type=float, default=None, help="모든 어스펙트에 적용할 고정 orb (기본: 어스펙트별 표준값)")
    p_asp.add_argument("--cusps", help="1~12하우스 커스프 절대황경도 12개, 콤마로 구분")
    p_asp.set_defaults(func=cmd_aspects)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
