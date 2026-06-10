"""Game logic for the pick-a-5 budget model."""
import json
import os
from collections import Counter
from .config import FORMATIONS, BUDGET, MAX_STARTERS_PER_TEAM, MAX_SUBS_PER_TEAM, SCORING, FIFA_ELO

_BASE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_BASE, "players.json"), encoding="utf-8") as f:
    PLAYERS = json.load(f)

PLAYERS_BY_ID = {p["id"]: p for p in PLAYERS}


_ELO_MID = 1600    # roughly average WC team
_ELO_SCALE = 1500  # divisor that gives ±~25% range across the WC field


def _elo_multiplier(opponent_elo):
    """Tougher opponent → lower multiplier (cheaper players, less expected output)."""
    raw = 1.0 + (_ELO_MID - opponent_elo) / _ELO_SCALE
    return max(0.75, min(1.25, raw))


def adjust_pool_values(pool, fixtures):
    """Return new pool list with values scaled by opponent ELO difficulty."""
    opp_elo = {}
    for fx in fixtures:
        home_elo = FIFA_ELO.get(fx.home_team, _ELO_MID)
        away_elo = FIFA_ELO.get(fx.away_team, _ELO_MID)
        opp_elo[fx.home_team] = away_elo
        opp_elo[fx.away_team] = home_elo
    adjusted = []
    for p in pool:
        mult = _elo_multiplier(opp_elo.get(p["team"], _ELO_MID))
        adjusted.append({**p, "value": max(1, round(p["value"] * mult))})
    return adjusted


def players_for_teams(teams):
    """All players whose national team is in `teams`, sorted by value desc."""
    teams = set(teams)
    out = [p for p in PLAYERS if p["team"] in teams]
    out.sort(key=lambda p: (-p["value"], p["name"]))
    return out


_SUB_POS_ORDER = ["GK", "DEF", "MID", "FWD"]


def sub_slot_roles(formation):
    """Map sub slot numbers to roles based on the formation's unique positions."""
    shape = FORMATIONS[formation]
    unique = [p for p in _SUB_POS_ORDER if p in shape]
    return {5 + i: role for i, role in enumerate(unique)}


def min_lineup_cost(pool):
    """Cheapest valid 5-starter + 4-sub lineup from pool. Used to floor the budget."""
    by_pos = {}
    for p in pool:
        by_pos.setdefault(p["pos"], []).append(p["value"])
    for pos in by_pos:
        by_pos[pos].sort()

    sub_cost = sum(by_pos.get(pos, [999])[0] for pos in ("GK", "DEF", "MID", "FWD"))

    min_start = float("inf")
    for shape in FORMATIONS.values():
        needed = Counter(shape)
        cost = 0
        valid = True
        for pos, count in needed.items():
            vals = by_pos.get(pos, [])
            if len(vals) < count:
                valid = False
                break
            cost += sum(vals[:count])
        if valid:
            min_start = min(min_start, cost)

    if min_start == float("inf"):
        return BUDGET
    return sub_cost + min_start


def validate_lineup(formation, picks, budget=BUDGET,
                    max_starters=MAX_STARTERS_PER_TEAM, max_subs=MAX_SUBS_PER_TEAM):
    """
    formation: key in FORMATIONS
    picks: list of dicts {slot, role, player_id}
      slots 0-4  → starting XI (must match formation length)
      slots 5-8  → subs bench (optional, each must match SUB_SLOT_ROLE)
    budget: the picking user's personal budget (base + referral bonus)
    Returns (ok, message, total_value).
    """
    if formation not in FORMATIONS:
        return False, "Unknown formation.", 0
    shape = FORMATIONS[formation]

    starter_picks = [p for p in picks if int(p["slot"]) < 5]
    sub_picks     = [p for p in picks if int(p["slot"]) >= 5]

    if len(starter_picks) != len(shape):
        return False, f"Pick all {len(shape)} starting positions.", 0

    seen_slots = set()
    seen_players = set()
    starter_team_counts = Counter()
    # Track which nations have starters in each role, for sub nation-matching
    starter_nations_by_role = {}
    total = 0

    for pk in starter_picks:
        slot = int(pk["slot"])
        if slot in seen_slots:
            return False, "Duplicate slot.", 0
        seen_slots.add(slot)
        if not (0 <= slot < len(shape)):
            return False, "Invalid slot.", 0
        player = PLAYERS_BY_ID.get(int(pk["player_id"]))
        if not player:
            return False, "Unknown player.", 0
        if player["id"] in seen_players:
            return False, f"{player['name']} picked twice.", 0
        seen_players.add(player["id"])
        role = shape[slot]
        if role != player["pos"]:
            return False, f"{player['name']} ({player['pos']}) can't fill a {role} slot.", 0
        starter_team_counts[player["team"]] += 1
        starter_nations_by_role.setdefault(role, set()).add(player["team"])
        total += player["value"]

    slot_role_map = sub_slot_roles(formation)
    for pk in sub_picks:
        slot = int(pk["slot"])
        if slot in seen_slots:
            return False, "Duplicate sub slot.", 0
        seen_slots.add(slot)
        expected = slot_role_map.get(slot)
        if not expected:
            return False, "Invalid sub slot.", 0
        player = PLAYERS_BY_ID.get(int(pk["player_id"]))
        if not player:
            return False, "Unknown player.", 0
        if player["id"] in seen_players:
            return False, f"{player['name']} picked twice.", 0
        seen_players.add(player["id"])
        if player["pos"] != expected:
            return False, f"{player['name']} ({player['pos']}) can't fill the {expected} sub slot.", 0
        # Sub must be from the same nation as the starter in this role
        valid_nations = starter_nations_by_role.get(expected, set())
        if player["team"] not in valid_nations:
            return False, f"{player['name']} ({player['team']}) must be from the same nation as your {expected} starter.", 0
        total += player["value"]

    over_start = [t for t, c in starter_team_counts.items() if c > max_starters]
    if over_start:
        return False, f"Max {max_starters} starters from one nation ({over_start[0]} has more).", 0
    if total > budget:
        return False, f"Over budget: {total}/{budget}.", total
    return True, "ok", total


def score_player(result, pos):
    if result is None:
        return 0.0
    pts = 0.0
    pts += result.goals * SCORING["goal"]
    pts += result.assists * SCORING["assist"]
    if result.clean_sheet:
        pts += SCORING["clean_sheet_gk_def"] if pos in ("GK", "DEF") else (
            SCORING["clean_sheet_mid"] if pos == "MID" else 0)
    pts += result.yellows * SCORING["yellow"]
    pts += result.reds * SCORING["red"]
    return pts


def score_entry(picks, results_by_player):
    """
    Score a lineup with same-nation auto-subs.
    If a starter's result has played=False, their bench player of the same role
    AND same nation replaces them. Cross-nation subs never trigger.
    """
    starter_picks = [p for p in picks if p.slot < 5]
    # bench keyed by role, only one sub per role
    sub_by_role = {p.role: p for p in picks if p.slot >= 5}

    total = 0.0
    for pk in starter_picks:
        player = PLAYERS_BY_ID.get(pk.player_id)
        if not player:
            continue
        result = results_by_player.get(pk.player_id)
        did_not_play = result is not None and not getattr(result, "played", True)

        if did_not_play:
            sub_pk = sub_by_role.get(pk.role)
            if sub_pk:
                sub_player = PLAYERS_BY_ID.get(sub_pk.player_id)
                # Only sub in if same nation — prevents cheap-starter / expensive-bench exploit
                if sub_player and sub_player["team"] == player["team"]:
                    sub_result = results_by_player.get(sub_pk.player_id)
                    total += score_player(sub_result, sub_player["pos"])
                    continue
            # no valid same-nation sub → starter scores 0
        else:
            total += score_player(result, player["pos"])

    return round(total, 1)
