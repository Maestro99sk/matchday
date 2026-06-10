"""Game logic for the pick-a-5 budget model."""
import json
import os
from collections import Counter
from .config import FORMATIONS, BUDGET, MAX_STARTERS_PER_TEAM, MAX_SUBS_PER_TEAM, SCORING

_BASE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_BASE, "players.json"), encoding="utf-8") as f:
    PLAYERS = json.load(f)

PLAYERS_BY_ID = {p["id"]: p for p in PLAYERS}


def players_for_teams(teams):
    """All players whose national team is in `teams`, sorted by value desc."""
    teams = set(teams)
    out = [p for p in PLAYERS if p["team"] in teams]
    out.sort(key=lambda p: (-p["value"], p["name"]))
    return out


# Slot indices 5-8 are the subs bench: one per position in this order
SUB_SLOT_ROLE = {5: "GK", 6: "DEF", 7: "MID", 8: "FWD"}


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
    sub_team_counts = Counter()
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
        if shape[slot] != player["pos"]:
            return False, f"{player['name']} ({player['pos']}) can't fill a {shape[slot]} slot.", 0
        starter_team_counts[player["team"]] += 1
        total += player["value"]

    for pk in sub_picks:
        slot = int(pk["slot"])
        if slot in seen_slots:
            return False, "Duplicate sub slot.", 0
        seen_slots.add(slot)
        expected = SUB_SLOT_ROLE.get(slot)
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
        sub_team_counts[player["team"]] += 1
        total += player["value"]

    over_start = [t for t, c in starter_team_counts.items() if c > max_starters]
    if over_start:
        return False, f"Max {max_starters} starters from one nation ({over_start[0]} has more).", 0
    over_subs = [t for t, c in sub_team_counts.items() if c > max_subs]
    if over_subs:
        return False, f"Max {max_subs} sub from one nation ({over_subs[0]} has more).", 0
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
    """Flat lineup sum: each picked player earns their event points."""
    total = 0.0
    for pk in picks:
        player = PLAYERS_BY_ID.get(pk.player_id)
        if not player:
            continue
        total += score_player(results_by_player.get(pk.player_id), player["pos"])
    return round(total, 1)
