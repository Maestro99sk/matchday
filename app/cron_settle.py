"""
Cron script: auto-settle any locked, unsettled matchday.

Run every 30 minutes via cron:
  */30 * * * * cd /var/www/matchday && source venv/bin/activate && python3 -m app.cron_settle >> /var/log/matchday_settle.log 2>&1
"""
import os
from datetime import datetime

# Load .env so API keys are available outside systemd
_env_path = "/var/www/matchday/.env"
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

from . import create_app
from .models import db, Matchday, Result, Entry
from .game import players_for_teams, score_entry
from .api_client import fetch_fixture_stats, match_api_to_pool


def run():
    app = create_app()
    with app.app_context():
        now = datetime.utcnow()
        pending = Matchday.query.filter_by(settled=False).all()
        eligible = [m for m in pending if m.lock_time and now >= m.lock_time]

        if not eligible:
            print(f"[{now:%Y-%m-%d %H:%M}] No unsettled locked matchdays.")
            return

        for md in eligible:
            print(f"[{now:%Y-%m-%d %H:%M}] Attempting to settle: {md.label} ...")
            errors = []
            merged = {}

            for fx in md.fixtures:
                api_stats, err = fetch_fixture_stats(fx.home_team, fx.away_team, md.date)
                if err:
                    errors.append(f"{fx.home_team} v {fx.away_team}: {err}")
                    continue
                fixture_pool = players_for_teams({fx.home_team, fx.away_team})
                for player, stats in match_api_to_pool(api_stats, fixture_pool):
                    if any([stats["goals"], stats["assists"],
                            stats["yellows"], stats["reds"], stats["clean_sheet"]]):
                        merged[player["id"]] = stats

            # If every fixture errored (e.g. not finished yet), skip entirely
            if errors and not merged:
                print(f"  Skipping — all fixtures blocked: {'; '.join(errors)}")
                continue

            # Partial errors (some fixtures done, some not) — settle what we have
            Result.query.filter_by(matchday_id=md.id).delete()
            for pid, s in merged.items():
                db.session.add(Result(
                    matchday_id=md.id, player_id=pid,
                    goals=s["goals"], assists=s["assists"], clean_sheet=s["clean_sheet"],
                    yellows=s["yellows"], reds=s["reds"],
                    played=s.get("played", True),
                ))
            db.session.commit()

            results = {r.player_id: r for r in Result.query.filter_by(matchday_id=md.id).all()}
            for e in Entry.query.filter_by(matchday_id=md.id).all():
                e.score = score_entry(e.picks, results)
            md.settled = True
            db.session.commit()

            msg = f"  Settled {md.label} — {len(merged)} players with stats."
            if errors:
                msg += f" Partial errors: {'; '.join(errors)}"
            print(msg)


if __name__ == "__main__":
    run()
