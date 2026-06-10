from datetime import datetime, date

MATCHDAYS = [
    {
        "label": "June 11",
        "date": date(2026, 6, 11),
        "lock": datetime(2026, 6, 11, 19, 0),
        "fixtures": [
            ("Mexico", "South Africa"),
        ],
    },
    {
        "label": "June 12",
        "date": date(2026, 6, 12),
        "lock": datetime(2026, 6, 12, 2, 0),
        "fixtures": [
            ("South Korea", "Czech Republic"),
            ("Canada", "Bosnia and Herzegovina"),
        ],
    },
    {
        "label": "June 13",
        "date": date(2026, 6, 13),
        "lock": datetime(2026, 6, 13, 1, 0),
        "fixtures": [
            ("United States", "Paraguay"),
            ("Qatar", "Switzerland"),
            ("Brazil", "Morocco"),
        ],
    },
    {
        "label": "June 14",
        "date": date(2026, 6, 14),
        "lock": datetime(2026, 6, 14, 1, 0),
        "fixtures": [
            ("Haiti", "Scotland"),
            ("Australia", "Turkey"),
            ("Germany", "Curacao"),
            ("Netherlands", "Japan"),
            ("Ivory Coast", "Ecuador"),
        ],
    },
    {
        "label": "June 15",
        "date": date(2026, 6, 15),
        "lock": datetime(2026, 6, 15, 2, 0),
        "fixtures": [
            ("Sweden", "Tunisia"),
            ("Spain", "Cape Verde"),
            ("Belgium", "Egypt"),
            ("Saudi Arabia", "Uruguay"),
        ],
    },
    {
        "label": "June 16",
        "date": date(2026, 6, 16),
        "lock": datetime(2026, 6, 16, 1, 0),
        "fixtures": [
            ("Iran", "New Zealand"),
            ("France", "Senegal"),
            ("Iraq", "Norway"),
        ],
    },
    {
        "label": "June 17",
        "date": date(2026, 6, 17),
        "lock": datetime(2026, 6, 17, 1, 0),
        "fixtures": [
            ("Argentina", "Algeria"),
            ("Austria", "Jordan"),
            ("Portugal", "DR Congo"),
            ("England", "Croatia"),
            ("Ghana", "Panama"),
        ],
    },
    {
        "label": "June 18",
        "date": date(2026, 6, 18),
        "lock": datetime(2026, 6, 18, 2, 0),
        "fixtures": [
            ("Uzbekistan", "Colombia"),
            ("Czech Republic", "South Africa"),
            ("Switzerland", "Bosnia and Herzegovina"),
            ("Canada", "Qatar"),
        ],
    },
    {
        "label": "June 19",
        "date": date(2026, 6, 19),
        "lock": datetime(2026, 6, 19, 1, 0),
        "fixtures": [
            ("Mexico", "South Korea"),
            ("United States", "Australia"),
            ("Scotland", "Morocco"),
        ],
    },
    {
        "label": "June 20",
        "date": date(2026, 6, 20),
        "lock": datetime(2026, 6, 20, 0, 30),
        "fixtures": [
            ("Brazil", "Haiti"),
            ("Turkey", "Paraguay"),
            ("Netherlands", "Sweden"),
            ("Germany", "Ivory Coast"),
        ],
    },
    {
        "label": "June 21",
        "date": date(2026, 6, 21),
        "lock": datetime(2026, 6, 21, 0, 0),
        "fixtures": [
            ("Ecuador", "Curacao"),
            ("Tunisia", "Japan"),
            ("Spain", "Saudi Arabia"),
            ("Belgium", "Iran"),
            ("Uruguay", "Cape Verde"),
        ],
    },
    {
        "label": "June 22",
        "date": date(2026, 6, 22),
        "lock": datetime(2026, 6, 22, 1, 0),
        "fixtures": [
            ("New Zealand", "Egypt"),
            ("Argentina", "Austria"),
            ("France", "Iraq"),
        ],
    },
    {
        "label": "June 23",
        "date": date(2026, 6, 23),
        "lock": datetime(2026, 6, 23, 0, 0),
        "fixtures": [
            ("Norway", "Senegal"),
            ("Jordan", "Algeria"),
            ("Portugal", "Uzbekistan"),
            ("England", "Ghana"),
            ("Panama", "Croatia"),
        ],
    },
    {
        "label": "June 24",
        "date": date(2026, 6, 24),
        "lock": datetime(2026, 6, 24, 2, 0),
        "fixtures": [
            ("Colombia", "DR Congo"),
            ("Switzerland", "Canada"),
            ("Bosnia and Herzegovina", "Qatar"),
            ("Morocco", "Haiti"),
            ("Scotland", "Brazil"),
        ],
    },
    {
        "label": "June 25",
        "date": date(2026, 6, 25),
        "lock": datetime(2026, 6, 25, 1, 0),
        "fixtures": [
            ("South Africa", "South Korea"),
            ("Czech Republic", "Mexico"),
            ("Curacao", "Ivory Coast"),
            ("Ecuador", "Germany"),
            ("Tunisia", "Netherlands"),
            ("Japan", "Sweden"),
        ],
    },
    {
        "label": "June 26",
        "date": date(2026, 6, 26),
        "lock": datetime(2026, 6, 26, 2, 0),
        "fixtures": [
            ("Turkey", "United States"),
            ("Paraguay", "Australia"),
            ("Norway", "France"),
            ("Senegal", "Iraq"),
        ],
    },
    {
        "label": "June 27",
        "date": date(2026, 6, 27),
        "lock": datetime(2026, 6, 27, 0, 0),
        "fixtures": [
            ("Cape Verde", "Saudi Arabia"),
            ("Uruguay", "Spain"),
            ("New Zealand", "Belgium"),
            ("Egypt", "Iran"),
            ("Panama", "England"),
            ("Croatia", "Ghana"),
            ("Colombia", "Portugal"),
            ("DR Congo", "Uzbekistan"),
        ],
    },
    {
        "label": "June 28",
        "date": date(2026, 6, 28),
        "lock": datetime(2026, 6, 28, 2, 0),
        "fixtures": [
            ("Algeria", "Austria"),
            ("Jordan", "Argentina"),
        ],
    },
]

# ---- 5-a-side formations (one GK each).
FORMATIONS = {
    "1-2-1": ["GK", "DEF", "MID", "MID", "FWD"],
    "2-1-1": ["GK", "DEF", "DEF", "MID", "FWD"],
    "1-1-2": ["GK", "DEF", "MID", "FWD", "FWD"],
    "2-2":   ["GK", "DEF", "DEF", "FWD", "FWD"],
    "3-1":   ["GK", "DEF", "DEF", "DEF", "FWD"],
    "1-3":   ["GK", "DEF", "FWD", "FWD", "FWD"],
}

BUDGET = 500
MAX_STARTERS_PER_TEAM = 2
MAX_SUBS_PER_TEAM = 1

REFERRAL_BONUS_PCT = 0.02
REFERRAL_BONUS_CAP_PCT = 0.20


def budget_for(referral_count):
    bonus = min(referral_count * REFERRAL_BONUS_PCT, REFERRAL_BONUS_CAP_PCT)
    return round(BUDGET * (1 + bonus))


def limits_for_pool(num_teams):
    """Dynamic per-team limits based on how many nations are in the day's pool."""
    if num_teams <= 2:
        return 3, 2   # max_starters, max_subs — single game day
    return MAX_STARTERS_PER_TEAM, MAX_SUBS_PER_TEAM


SCORING = {
    "goal": 10,
    "assist": 7,
    "clean_sheet_gk_def": 6,
    "clean_sheet_mid": 3,
    "yellow": -2,
    "red": -5,
}
