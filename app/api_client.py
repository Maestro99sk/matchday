"""API-Football (api-sports.io) integration for auto-settling matchdays.

Set API_FOOTBALL_KEY in the environment. Free tier: 100 requests/day.
World Cup 2026 = league_id 1, season 2026.
"""
import os
import unicodedata
from datetime import datetime, timedelta
from difflib import SequenceMatcher

import requests

BASE = "https://v3.football.api-sports.io"
WC_LEAGUE = 1
WC_SEASON = 2026

# Statuses that mean the match is fully over
FINISHED = {"FT", "AET", "PEN", "AWD", "WO"}

# Our team names sometimes differ from the API's
TEAM_ALIASES = {
    "United States":         ["USA", "United States", "US"],
    "South Korea":           ["Korea Republic", "South Korea"],
    "Bosnia and Herzegovina":["Bosnia", "Bosnia & Herzegovina", "Bosnia and Herzegovina"],
    "Ivory Coast":           ["Côte d'Ivoire", "Ivory Coast", "Cote d'Ivoire"],
    "Curacao":               ["Curaçao", "Curacao"],
    "Czech Republic":        ["Czechia", "Czech Republic"],
}


def _strip_accents(s):
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )


def _norm(s):
    return _strip_accents(s.lower().strip())


def _team_match(api_name, our_name):
    if _norm(api_name) == _norm(our_name):
        return True
    for alias in TEAM_ALIASES.get(our_name, []):
        if _norm(api_name) == _norm(alias):
            return True
    return SequenceMatcher(None, _norm(api_name), _norm(our_name)).ratio() > 0.82


def _player_score(api_name, our_name):
    a, b = _norm(api_name), _norm(our_name)
    full = SequenceMatcher(None, a, b).ratio()
    # also try matching on last name alone
    last_a = a.split()[-1] if a.split() else a
    last_b = b.split()[-1] if b.split() else b
    last = SequenceMatcher(None, last_a, last_b).ratio() * 0.85
    return max(full, last)


def _headers():
    return {"x-apisports-key": os.environ.get("API_FOOTBALL_KEY", "")}


def fetch_fixture_stats(home_team, away_team, match_date):
    """
    Fetch per-player stats for one fixture.

    Returns (stats_dict, error_string).
    stats_dict maps api_player_name -> {goals, assists, clean_sheet, yellows, reds}.
    On failure returns (None, error_string).
    """
    if not os.environ.get("API_FOOTBALL_KEY", ""):
        return None, "API_FOOTBALL_KEY environment variable not set."

    # --- find the fixture ---
    # Search a 3-day window centered on match_date. World Cup kickoffs late in
    # local-day can land on the previous or next UTC date depending on host city,
    # and the API indexes by the UTC kickoff date.
    candidates = []
    not_finished_status = None
    for offset in (0, -1, 1):
        d = match_date + timedelta(days=offset)
        try:
            r = requests.get(
                f"{BASE}/fixtures",
                params={"date": str(d), "league": WC_LEAGUE, "season": WC_SEASON},
                headers=_headers(),
                timeout=15,
            )
            r.raise_for_status()
        except requests.RequestException as e:
            return None, f"Network error: {e}"

        data = r.json()
        if data.get("errors"):
            return None, f"API error: {data['errors']}"

        for fx in data.get("response", []):
            h = fx["teams"]["home"]["name"]
            a = fx["teams"]["away"]["name"]
            if _team_match(h, home_team) and _team_match(a, away_team):
                status = fx["fixture"]["status"]["short"]
                if status in FINISHED:
                    candidates.append(fx)
                else:
                    not_finished_status = status

    fixture_id = None
    home_goals = away_goals = None
    if candidates:
        target_ts = datetime(match_date.year, match_date.month, match_date.day).timestamp()
        fx = min(candidates, key=lambda fx: abs(int(fx["fixture"]["timestamp"]) - target_ts))
        fixture_id = fx["fixture"]["id"]
        home_goals = fx["goals"]["home"] or 0
        away_goals = fx["goals"]["away"] or 0

    if fixture_id is None:
        if not_finished_status is not None:
            return None, f"{home_team} v {away_team}: match not finished yet (status: {not_finished_status})."
        return None, f"Fixture not found in API: {home_team} v {away_team} on {match_date}."

    # --- fetch player stats ---
    try:
        r = requests.get(
            f"{BASE}/fixtures/players",
            params={"fixture": fixture_id},
            headers=_headers(),
            timeout=15,
        )
        r.raise_for_status()
    except requests.RequestException as e:
        return None, f"Network error fetching player stats: {e}"

    pdata = r.json()
    if pdata.get("errors"):
        return None, f"API error fetching player stats: {pdata['errors']}"

    # --- fetch starting lineup to determine who played ---
    starters_set = set()
    try:
        lr = requests.get(
            f"{BASE}/fixtures/lineups",
            params={"fixture": fixture_id},
            headers=_headers(),
            timeout=15,
        )
        lr.raise_for_status()
        for team_block in lr.json().get("response", []):
            for p in team_block.get("startXI", []):
                name = (p.get("player") or {}).get("name")
                if name:
                    starters_set.add(_norm(name))
    except requests.RequestException:
        pass  # if lineup fetch fails, assume everyone played

    stats = {}
    for team_block in pdata.get("response", []):
        api_team = team_block["team"]["name"]
        is_home = _team_match(api_team, home_team)
        conceded = away_goals if is_home else home_goals
        clean_sheet = conceded == 0

        for p in team_block.get("players", []):
            name = p["player"]["name"]
            s = (p.get("statistics") or [{}])[0]
            g_block = s.get("goals") or {}
            c_block = s.get("cards") or {}
            mins = (s.get("games") or {}).get("minutes") or 0
            # played = was in starting XI or came on as sub (minutes > 0)
            played = bool(starters_set and _norm(name) in starters_set) or int(mins) > 0
            stats[name] = {
                "goals":       int(g_block.get("total") or 0),
                "assists":     int(g_block.get("assists") or 0),
                "clean_sheet": clean_sheet,
                "yellows":     int(c_block.get("yellow") or 0),
                "reds":        int(c_block.get("red") or 0),
                "played":      played,
            }

    return stats, None


def match_api_to_pool(api_stats, pool_players, threshold=0.72):
    """
    Match API player names to our players.json entries.

    Returns list of (player_dict, stats_dict).
    Only includes players where something happened (goals/assists/cards)
    or they were on a clean-sheet team.
    """
    api_names = list(api_stats.keys())
    matched = []
    seen_api = set()

    for player in pool_players:
        our_name = player["name"]

        # exact match first (after normalisation)
        exact = next(
            (n for n in api_names if _norm(n) == _norm(our_name)),
            None,
        )
        if exact and exact not in seen_api:
            seen_api.add(exact)
            matched.append((player, api_stats[exact]))
            continue

        # fuzzy
        best = max(api_names, key=lambda n: _player_score(n, our_name), default=None)
        if best and best not in seen_api and _player_score(best, our_name) >= threshold:
            seen_api.add(best)
            matched.append((player, api_stats[best]))

    return matched
