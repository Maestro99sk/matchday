"""
World Cup 2026 group-stage fixtures (source: ESPN / NBC / Sky schedules).
Grouped into matchdays. Each matchday lists the fixtures played that calendar
day; the pick pool for a matchday is every player whose national team appears.

Only the opening matchdays are fully enumerated here. Add the remaining days in
the same shape and the app picks them up automatically — no code changes needed.

Dates are the real 2026 calendar dates. lock_time is the first kickoff (UTC-ish,
naive); adjust to your timezone handling as needed.
"""
from datetime import datetime, date

# (home, away)
MATCHDAYS = [
    {
        "label": "Matchday 1 - June 11",
        "date": date(2026, 6, 11),
        "lock": datetime(2026, 6, 11, 19, 0),
        "fixtures": [("Mexico", "South Africa"), ("South Korea", "Czech Republic")],
    },
    {
        "label": "Matchday 2 - June 12",
        "date": date(2026, 6, 12),
        "lock": datetime(2026, 6, 12, 19, 0),
        "fixtures": [("Canada", "Bosnia and Herzegovina"), ("United States", "Paraguay")],
    },
    {
        "label": "Matchday 3 - June 13",
        "date": date(2026, 6, 13),
        "lock": datetime(2026, 6, 13, 16, 0),
        "fixtures": [
            ("Qatar", "Switzerland"),
            ("Brazil", "Morocco"),
            ("Haiti", "Scotland"),
            ("Australia", "Turkey"),
        ],
    },
    {
        "label": "Matchday 4 - June 14",
        "date": date(2026, 6, 14),
        "lock": datetime(2026, 6, 14, 16, 0),
        "fixtures": [
            ("Germany", "Curacao"),
            ("Spain", "Egypt"),
            ("Argentina", "Algeria"),
            ("Portugal", "Senegal"),
        ],
    },
    {
        "label": "Matchday 5 - June 15",
        "date": date(2026, 6, 15),
        "lock": datetime(2026, 6, 15, 16, 0),
        "fixtures": [
            ("Belgium", "Ivory Coast"),
            ("Netherlands", "Japan"),
            ("Croatia", "Ghana"),
            ("Uruguay", "Panama"),
        ],
    },
    {
        "label": "Matchday 6 - June 16",
        "date": date(2026, 6, 16),
        "lock": datetime(2026, 6, 16, 16, 0),
        "fixtures": [
            ("Colombia", "Uzbekistan"),
            ("England", "Iran"),
            ("Ecuador", "Norway"),
            ("Austria", "Saudi Arabia"),
        ],
    },
]

# ---- 5-a-side formations (one GK each). Slot coords are % on a vertical pitch.
FORMATIONS = {
    "1-2-1": ["GK", "DEF", "MID", "MID", "FWD"],
    "2-1-1": ["GK", "DEF", "DEF", "MID", "FWD"],
    "1-1-2": ["GK", "DEF", "MID", "FWD", "FWD"],
    "2-2":   ["GK", "DEF", "DEF", "FWD", "FWD"],
    "3-1":   ["GK", "DEF", "DEF", "DEF", "FWD"],
    "1-3":   ["GK", "DEF", "FWD", "FWD", "FWD"],
}

BUDGET = 500              # per manager per matchday (base; includes budget for 4 subs)
MAX_STARTERS_PER_TEAM = 2   # at most 2 starters from one national team
MAX_SUBS_PER_TEAM = 1       # at most 1 sub from one national team

# referrals: each confirmed referral adds this fraction of the base budget,
# capped so it stays bounded and the league remains meaningful.
REFERRAL_BONUS_PCT = 0.02     # per referral
REFERRAL_BONUS_CAP_PCT = 0.20 # never more than this total


def budget_for(referral_count):
    """Personal matchday budget given a user's confirmed referral count."""
    bonus = min(referral_count * REFERRAL_BONUS_PCT, REFERRAL_BONUS_CAP_PCT)
    return round(BUDGET * (1 + bonus))

# scoring weights per real-world event
SCORING = {
    "goal": 10,
    "assist": 7,
    "clean_sheet_gk_def": 6,
    "clean_sheet_mid": 3,
    "yellow": -2,
    "red": -5,
}
