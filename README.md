# Matchday ⚽ — World Cup pick-a-5

Each matchday: choose a 5-a-side formation (always one keeper), fill it with five
players from that day's games while staying under budget, max two per nation.
Score points on goals, assists, clean sheets and cards. Friends leagues + world ranking.

## Run locally

```bash
cd matchday2
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m app.seed      # creates db + loads the real WC fixtures
python run.py           # http://127.0.0.1:5000
```

Open on your phone over the same wifi via `http://<your-ip>:5000`.

## First steps

1. **Register** — the *first* account is the admin (it settles matchdays at `/admin/settle`).
2. **Create a league**, share the 6-char code, friends join by it.
3. Hit **Play** on the open matchday: cycle formations with the arrows, tap a slot,
   pick a player from the day's pool. Stay under budget (300). **Confirm lineup.**
4. After the games, the admin enters results at **`/admin/settle`** and every lineup
   is scored automatically; tables + ranking update.

## The game

- **Budget**: 300 per matchday (set in `app/config.py`).
- **Formations** (one GK each): 1-2-1, 2-1-1, 1-1-2, 2-2, 3-1, 1-3.
- **Squad rule**: max 2 players from one nation.
- **Scoring**: goal +10, assist +7, clean sheet +6 (GK/DEF) / +3 (MID),
  yellow −2, red −5. All in `app/config.py`.
- **Player values**: forwards > midfielders > defenders > keepers, scaled by team
  strength (in `players.json`, 1,264 players, all 48 squads).

## Data

- `app/players.json` — every player, position, club, rating, value. Regenerate or
  hand-edit as squads change.
- `app/config.py` — fixtures by matchday. Only the opening matchdays are filled in;
  add the rest in the same shape and the app picks them up. **This is the main thing
  to extend before the tournament runs its full course.**

## Referrals

Every account gets a unique referral link (shown on the dashboard). When someone
signs up through it, the referrer's transfer budget goes up — additively, with a
ceiling, so it stays bounded and leagues stay competitive. The exact rate and cap
live in `app/config.py` (`REFERRAL_BONUS_PCT`, `REFERRAL_BONUS_CAP_PCT`); the
mechanic is deliberately not spelled out in the UI.

Abuse guard is intentionally light for launch: self-referral is ignored, and a new
signup sharing the referrer's IP doesn't count. This stops casual same-device
farming but isn't bulletproof (a VPN defeats it). Real protection (email/phone
verification) is a fast-follow, not a Thursday item.

## Deploy (Render / Railway / Fly)

- `Procfile` runs `gunicorn "app:create_app()"`.
- Set `SECRET_KEY` (any long random string) and `DATABASE_URL` (Postgres) as env vars.
  Without `DATABASE_URL` it uses local SQLite, which **won't survive redeploys** — use
  a managed Postgres in production. The app auto-rewrites `postgres://` → `postgresql://`.
- After first deploy, run `python -m app.seed` once against the production DB.

## Ads

AdSense approval is too slow for launch. The ad slots/flow can be added to the
templates; sign up for Monetag or Adsterra (same-day approval) and paste their zone
script where you want banners.

## Still to do (not code — decisions/ops)

- Add remaining group-stage fixtures to `app/config.py`.
- Stand up Postgres + deploy; set env vars; seed once.
- Wire an ad network.
- Plan results entry: manual via `/admin/settle` for early matchdays; a stats API
  later (write `Result` rows, then the same scoring loop runs).
