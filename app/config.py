from datetime import datetime, date

MATCHDAYS = [
    {
        "label": "June 10 (Trial)",
        "date": date(2026, 6, 10),
        "lock": datetime(2026, 6, 10, 19, 30),  # 3:30pm ET — 30 mins before 4pm ET kickoff
        "fixtures": [
            ("England", "Costa Rica"),           # International Friendly, 4pm ET
        ],
    },
    {
        "label": "June 11",
        "date": date(2026, 6, 11),
        "lock": datetime(2026, 6, 11, 17, 0),   # 1pm ET — before 3pm ET opener
        "fixtures": [
            ("Mexico", "South Africa"),           # 3pm ET
            ("South Korea", "Czech Republic"),    # 10pm ET
        ],
    },
    {
        "label": "June 12",
        "date": date(2026, 6, 12),
        "lock": datetime(2026, 6, 12, 17, 0),   # 1pm ET
        "fixtures": [
            ("Canada", "Bosnia and Herzegovina"), # 3pm ET
            ("United States", "Paraguay"),        # 9pm ET
        ],
    },
    {
        "label": "June 13",
        "date": date(2026, 6, 13),
        "lock": datetime(2026, 6, 13, 17, 0),   # 1pm ET
        "fixtures": [
            ("Qatar", "Switzerland"),             # 3pm ET
            ("Brazil", "Morocco"),                # 6pm ET
            ("Haiti", "Scotland"),                # 9pm ET
        ],
    },
    {
        "label": "June 14",
        "date": date(2026, 6, 14),
        "lock": datetime(2026, 6, 14, 2, 0),    # 10pm ET June 13 — before midnight first game
        "fixtures": [
            ("Australia", "Turkey"),              # 12am ET (9pm PT June 13)
            ("Germany", "Curacao"),               # 1pm ET
            ("Japan", "Netherlands"),             # 4pm ET
            ("Ivory Coast", "Ecuador"),           # 7pm ET
            ("Sweden", "Tunisia"),                # 10pm ET
        ],
    },
    {
        "label": "June 15",
        "date": date(2026, 6, 15),
        "lock": datetime(2026, 6, 15, 14, 0),   # 10am ET — before noon first game
        "fixtures": [
            ("Spain", "Cape Verde"),              # 12pm ET
            ("Belgium", "Egypt"),                 # 3pm ET
            ("Saudi Arabia", "Uruguay"),          # 6pm ET
            ("Iran", "New Zealand"),              # 9pm ET
        ],
    },
    {
        "label": "June 16",
        "date": date(2026, 6, 16),
        "lock": datetime(2026, 6, 16, 17, 0),   # 1pm ET
        "fixtures": [
            ("France", "Senegal"),                # 3pm ET
            ("Iraq", "Norway"),                   # 6pm ET
            ("Argentina", "Algeria"),             # 9pm ET
        ],
    },
    {
        "label": "June 17",
        "date": date(2026, 6, 17),
        "lock": datetime(2026, 6, 17, 2, 0),    # 10pm ET June 16 — before midnight first game
        "fixtures": [
            ("Austria", "Jordan"),                # 12am ET (9pm PT June 16)
            ("Portugal", "DR Congo"),             # 1pm ET
            ("England", "Croatia"),               # 4pm ET
            ("Ghana", "Panama"),                  # 7pm ET
            ("Uzbekistan", "Colombia"),           # 10pm ET
        ],
    },
    {
        "label": "June 18",
        "date": date(2026, 6, 18),
        "lock": datetime(2026, 6, 18, 14, 0),   # 10am ET — before noon first game
        "fixtures": [
            ("Czech Republic", "South Africa"),   # 12pm ET
            ("Switzerland", "Bosnia and Herzegovina"), # 3pm ET
            ("Canada", "Qatar"),                  # 6pm ET
            ("Mexico", "South Korea"),            # 9pm ET
        ],
    },
    {
        "label": "June 19",
        "date": date(2026, 6, 19),
        "lock": datetime(2026, 6, 19, 17, 0),   # 1pm ET
        "fixtures": [
            ("United States", "Australia"),       # 3pm ET
            ("Scotland", "Morocco"),              # 6pm ET
            ("Brazil", "Haiti"),                  # 8:30pm ET
            ("Turkey", "Paraguay"),               # 11pm ET
        ],
    },
    {
        "label": "June 20",
        "date": date(2026, 6, 20),
        "lock": datetime(2026, 6, 20, 16, 0),   # noon ET — before 1pm first game
        "fixtures": [
            ("Netherlands", "Sweden"),            # 1pm ET
            ("Germany", "Ivory Coast"),           # 4pm ET
            ("Ecuador", "Curacao"),               # 8pm ET
        ],
    },
    {
        "label": "June 21",
        "date": date(2026, 6, 21),
        "lock": datetime(2026, 6, 21, 2, 0),    # 10pm ET June 20 — before midnight first game
        "fixtures": [
            ("Tunisia", "Japan"),                 # 12am ET (9pm PT June 20)
            ("Spain", "Saudi Arabia"),            # 12pm ET
            ("Belgium", "Iran"),                  # 3pm ET
            ("Uruguay", "Cape Verde"),            # 6pm ET
            ("Egypt", "New Zealand"),             # 9pm ET
        ],
    },
    {
        "label": "June 22",
        "date": date(2026, 6, 22),
        "lock": datetime(2026, 6, 22, 16, 0),   # noon ET — before 1pm first game
        "fixtures": [
            ("Argentina", "Austria"),             # 1pm ET
            ("France", "Iraq"),                   # 5pm ET
            ("Senegal", "Norway"),                # 8pm ET
            ("Algeria", "Jordan"),                # 11pm ET
        ],
    },
    {
        "label": "June 23",
        "date": date(2026, 6, 23),
        "lock": datetime(2026, 6, 23, 16, 0),   # noon ET — before 1pm first game
        "fixtures": [
            ("Portugal", "Uzbekistan"),           # 1pm ET
            ("England", "Ghana"),                 # 4pm ET
            ("Croatia", "Panama"),                # 7pm ET
            ("Colombia", "DR Congo"),             # 10pm ET
        ],
    },
    {
        "label": "June 24",
        "date": date(2026, 6, 24),
        "lock": datetime(2026, 6, 24, 17, 0),   # 1pm ET — before simultaneous 3pm kickoffs
        "fixtures": [
            ("Bosnia and Herzegovina", "Qatar"),  # 3pm ET (simultaneous)
            ("Switzerland", "Canada"),            # 3pm ET (simultaneous)
            ("Morocco", "Haiti"),                 # 6pm ET (simultaneous)
            ("Brazil", "Scotland"),               # 6pm ET (simultaneous)
            ("Mexico", "Czech Republic"),         # 9pm ET (simultaneous)
            ("South Korea", "South Africa"),      # 9pm ET (simultaneous)
        ],
    },
    {
        "label": "June 25",
        "date": date(2026, 6, 25),
        "lock": datetime(2026, 6, 25, 18, 0),   # 2pm ET — before simultaneous 4pm kickoffs
        "fixtures": [
            ("Curacao", "Ivory Coast"),           # 4pm ET (simultaneous)
            ("Ecuador", "Germany"),               # 4pm ET (simultaneous)
            ("Japan", "Sweden"),                  # 7pm ET (simultaneous)
            ("Tunisia", "Netherlands"),           # 7pm ET (simultaneous)
            ("Paraguay", "Australia"),            # 10pm ET (simultaneous)
            ("Turkey", "United States"),          # 10pm ET (simultaneous)
        ],
    },
    {
        "label": "June 26",
        "date": date(2026, 6, 26),
        "lock": datetime(2026, 6, 26, 17, 0),   # 1pm ET — before simultaneous 3pm kickoffs
        "fixtures": [
            ("Iraq", "Senegal"),                  # 3pm ET (simultaneous)
            ("Norway", "France"),                 # 3pm ET (simultaneous)
            ("Cape Verde", "Saudi Arabia"),       # 8pm ET (simultaneous)
            ("Uruguay", "Spain"),                 # 8pm ET (simultaneous)
            ("Egypt", "Iran"),                    # 11pm ET (simultaneous)
            ("New Zealand", "Belgium"),           # 11pm ET (simultaneous)
        ],
    },
    {
        "label": "June 27",
        "date": date(2026, 6, 27),
        "lock": datetime(2026, 6, 27, 19, 0),   # 3pm ET — before simultaneous 5pm kickoffs
        "fixtures": [
            ("Ghana", "Croatia"),                 # 5pm ET (simultaneous)
            ("Panama", "England"),                # 5pm ET (simultaneous)
            ("Colombia", "Portugal"),             # 7:30pm ET (simultaneous)
            ("DR Congo", "Uzbekistan"),           # 7:30pm ET (simultaneous)
            ("Algeria", "Austria"),               # 10pm ET (simultaneous)
            ("Jordan", "Argentina"),              # 10pm ET (simultaneous)
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
