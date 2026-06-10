"""Matchday - World Cup pick-a-5 budget fantasy."""
import os, random, string
from functools import wraps
from datetime import datetime

from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, jsonify, abort)

from .models import (db, User, League, Membership, Matchday, Fixture, Result, Entry, Pick)
from .game import (PLAYERS, PLAYERS_BY_ID, players_for_teams, validate_lineup,
                   score_entry)
from .config import (FORMATIONS, BUDGET, MAX_STARTERS_PER_TEAM, MAX_SUBS_PER_TEAM,
                     SCORING, budget_for, limits_for_pool, REFERRAL_BONUS_PCT,
                     REFERRAL_BONUS_CAP_PCT, MATCHDAYS)
from .api_client import fetch_fixture_stats, match_api_to_pool


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-change-me")
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_url = os.environ.get("DATABASE_URL", "sqlite:///" + os.path.join(base, "matchday.db"))
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    def login_required(f):
        @wraps(f)
        def w(*a, **k):
            if "user_id" not in session:
                return redirect(url_for("login"))
            return f(*a, **k)
        return w

    def current_user():
        uid = session.get("user_id")
        return User.query.get(uid) if uid else None

    def gen_code(n=6):
        while True:
            c = "".join(random.choices(string.ascii_uppercase + string.digits, k=n))
            if not League.query.filter_by(code=c).first():
                return c

    def gen_ref_code(n=7):
        while True:
            c = "".join(random.choices(string.ascii_uppercase + string.digits, k=n))
            if not User.query.filter_by(referral_code=c).first():
                return c

    _FLAGS = {
        "Czech Republic":"🇨🇿","Mexico":"🇲🇽","South Africa":"🇿🇦","South Korea":"🇰🇷",
        "Canada":"🇨🇦","Bosnia and Herzegovina":"🇧🇦","United States":"🇺🇸","Paraguay":"🇵🇾",
        "Qatar":"🇶🇦","Switzerland":"🇨🇭","Brazil":"🇧🇷","Morocco":"🇲🇦","Haiti":"🇭🇹",
        "Scotland":"🏴󠁧󠁢󠁳󠁣󠁴󠁿","Australia":"🇦🇺","Turkey":"🇹🇷","Germany":"🇩🇪",
        "Curacao":"🇨🇼","Spain":"🇪🇸","Egypt":"🇪🇬","Argentina":"🇦🇷","Algeria":"🇩🇿",
        "Portugal":"🇵🇹","Senegal":"🇸🇳","Belgium":"🇧🇪","Ivory Coast":"🇨🇮",
        "Netherlands":"🇳🇱","Japan":"🇯🇵","Croatia":"🇭🇷","Ghana":"🇬🇭","Uruguay":"🇺🇾",
        "Panama":"🇵🇦","Colombia":"🇨🇴","Uzbekistan":"🇺🇿","England":"🏴󠁧󠁢󠁥󠁮󠁧󠁿",
        "Iran":"🇮🇷","Ecuador":"🇪🇨","Norway":"🇳🇴","Austria":"🇦🇹","Saudi Arabia":"🇸🇦",
        "France":"🇫🇷","Italy":"🇮🇹","Denmark":"🇩🇰","Serbia":"🇷🇸","Poland":"🇵🇱",
        "Ukraine":"🇺🇦","Wales":"🏴󠁧󠁢󠁷󠁬󠁳󠁿","Cameroon":"🇨🇲","Tunisia":"🇹🇳",
        "Nigeria":"🇳🇬","New Zealand":"🇳🇿","Chile":"🇨🇱","Peru":"🇵🇪",
        "Venezuela":"🇻🇪","Honduras":"🇭🇳","Costa Rica":"🇨🇷","Jamaica":"🇯🇲",
    }
    app.jinja_env.filters["teamflag"] = lambda t: _FLAGS.get(t, t[:3].upper())
    app.jinja_env.globals.update(current_user=current_user, BUDGET=BUDGET)

    # ---- auth ----
    @app.route("/")
    def index():
        return redirect(url_for("dashboard")) if current_user() else render_template("index.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        # referral code can arrive as ?ref=CODE (GET) and is carried through the form
        ref = request.values.get("ref", "").strip().upper()
        if request.method == "POST":
            u = request.form["username"].strip()
            p = request.form["password"]
            if not (3 <= len(u) <= 32):
                flash("Username must be 3-32 characters.", "error")
            elif len(p) < 6:
                flash("Password must be at least 6 characters.", "error")
            elif User.query.filter_by(username=u).first():
                flash("That username is taken.", "error")
            else:
                referrer = User.query.filter_by(referral_code=ref).first() if ref else None
                ip = (request.headers.get("X-Forwarded-For", request.remote_addr or "")
                      .split(",")[0].strip())
                user = User(username=u, referral_code=gen_ref_code(), signup_ip=ip)
                user.set_password(p)
                if referrer:
                    user.referred_by = referrer.id
                db.session.add(user)
                db.session.commit()
                # credit the referrer, but skip obvious self-farming:
                # ignore if the new signup shares the referrer's signup IP.
                if referrer and not (ip and referrer.signup_ip == ip):
                    referrer.referral_count = (referrer.referral_count or 0) + 1
                    db.session.commit()
                session["user_id"] = user.id
                return redirect(url_for("dashboard"))
        return render_template("register.html", ref=ref)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            user = User.query.filter_by(username=request.form["username"].strip()).first()
            if user and user.check_password(request.form["password"]):
                if not user.referral_code:        # backfill for pre-feature accounts
                    user.referral_code = gen_ref_code(); db.session.commit()
                session["user_id"] = user.id
                return redirect(url_for("dashboard"))
            flash("Invalid username or password.", "error")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear(); return redirect(url_for("index"))

    # ---- dashboard & leagues ----
    @app.route("/dashboard")
    @login_required
    def dashboard():
        u = current_user()
        lids = [m.league_id for m in u.memberships]
        leagues = League.query.filter(League.id.in_(lids)).all() if lids else []
        next_md = Matchday.query.filter_by(settled=False).order_by(Matchday.date).first()
        ranking = (db.session.query(User.username, db.func.sum(Entry.score).label("pts"))
                   .join(Entry, Entry.user_id == User.id).group_by(User.id)
                   .order_by(db.text("pts DESC")).limit(20).all())
        ref_link = url_for("register", ref=u.referral_code, _external=True) if u.referral_code else None
        my_budget = budget_for(u.referral_count or 0)
        at_cap = (u.referral_count or 0) * REFERRAL_BONUS_PCT >= REFERRAL_BONUS_CAP_PCT
        # find the user's team for the next matchday (first league with an entry)
        my_entry = None
        my_entry_league = None
        my_picks = []
        if next_md and lids:
            for lg in leagues:
                e = Entry.query.filter_by(user_id=u.id, league_id=lg.id, matchday_id=next_md.id).first()
                if e:
                    my_entry = e
                    my_entry_league = lg
                    for pk in e.picks:
                        player = PLAYERS_BY_ID.get(pk.player_id)
                        if player:
                            my_picks.append({"slot": pk.slot, "role": pk.role, "player": player})
                    break
        return render_template("dashboard.html", leagues=leagues, next_md=next_md,
                               ranking=ranking, ref_link=ref_link, base_budget=BUDGET,
                               my_budget=my_budget, ref_count=(u.referral_count or 0),
                               at_cap=at_cap, my_entry=my_entry,
                               my_entry_league=my_entry_league, my_picks=my_picks)

    @app.route("/league/create", methods=["POST"])
    @login_required
    def league_create():
        u = current_user()
        lg = League(name=request.form["name"].strip() or "Unnamed League",
                    code=gen_code(), owner_id=u.id)
        db.session.add(lg); db.session.commit()
        db.session.add(Membership(user_id=u.id, league_id=lg.id)); db.session.commit()
        return redirect(url_for("league_view", league_id=lg.id))

    @app.route("/league/join", methods=["POST"])
    @login_required
    def league_join():
        u = current_user()
        lg = League.query.filter_by(code=request.form["code"].strip().upper()).first()
        if not lg:
            flash("No league with that code.", "error")
            return redirect(url_for("dashboard"))
        if not Membership.query.filter_by(user_id=u.id, league_id=lg.id).first():
            db.session.add(Membership(user_id=u.id, league_id=lg.id)); db.session.commit()
        return redirect(url_for("league_view", league_id=lg.id))

    @app.route("/league/<int:league_id>")
    @login_required
    def league_view(league_id):
        u = current_user(); lg = League.query.get_or_404(league_id)
        if not Membership.query.filter_by(user_id=u.id, league_id=lg.id).first():
            abort(403)
        mids = [m.user_id for m in lg.memberships]
        members = User.query.filter(User.id.in_(mids)).all()
        table = []
        for m in members:
            tot = (db.session.query(db.func.coalesce(db.func.sum(Entry.score), 0.0))
                   .filter(Entry.user_id == m.id, Entry.league_id == lg.id).scalar())
            table.append({"user_id": m.id, "username": m.username, "score": round(tot, 1)})
        table.sort(key=lambda r: r["score"], reverse=True)
        next_md = Matchday.query.filter_by(settled=False).order_by(Matchday.date).first()
        display_md = next_md or Matchday.query.filter_by(settled=True).order_by(Matchday.date.desc()).first()
        return render_template("league.html", league=lg, table=table,
                               next_md=next_md, display_md=display_md, current_user_id=u.id)

    # ---- play ----
    @app.route("/play/<int:league_id>/<int:matchday_id>")
    @login_required
    def play(league_id, matchday_id):
        u = current_user()
        lg = League.query.get_or_404(league_id)
        md = Matchday.query.get_or_404(matchday_id)
        if not Membership.query.filter_by(user_id=u.id, league_id=lg.id).first():
            abort(403)
        locked = datetime.utcnow() >= md.lock_time
        teams = set()
        for fx in md.fixtures:
            teams.add(fx.home_team); teams.add(fx.away_team)
        pool = players_for_teams(teams)
        my_budget = budget_for(u.referral_count or 0)
        max_starters, max_subs = limits_for_pool(len(teams))
        entry = Entry.query.filter_by(user_id=u.id, league_id=lg.id, matchday_id=md.id).first()
        existing = None
        if entry:
            existing = {"formation": entry.formation,
                        "picks": [{"slot": p.slot, "role": p.role, "player_id": p.player_id}
                                  for p in entry.picks]}
        return render_template("play.html", league=lg, matchday=md,
                               fixtures=md.fixtures, pool=pool, locked=locked,
                               formations=FORMATIONS, existing=existing,
                               budget=my_budget, base_budget=BUDGET,
                               max_starters_per_team=max_starters,
                               max_subs_per_team=max_subs,
                               scoring=SCORING)

    @app.route("/play/<int:league_id>/<int:matchday_id>/submit", methods=["POST"])
    @login_required
    def play_submit(league_id, matchday_id):
        u = current_user()
        lg = League.query.get_or_404(league_id)
        md = Matchday.query.get_or_404(matchday_id)
        if not Membership.query.filter_by(user_id=u.id, league_id=lg.id).first():
            abort(403)
        if datetime.utcnow() >= md.lock_time:
            return jsonify(ok=False, msg="Locked - the games have kicked off."), 400
        data = request.get_json(force=True)
        formation = data.get("formation")
        picks = data.get("picks", [])
        # players must belong to today's teams
        teams = set()
        for fx in md.fixtures:
            teams.add(fx.home_team); teams.add(fx.away_team)
        for pk in picks:
            pl = PLAYERS_BY_ID.get(int(pk.get("player_id", -1)))
            if not pl or pl["team"] not in teams:
                return jsonify(ok=False, msg="A picked player isn't in today's games."), 400
        max_starters, max_subs = limits_for_pool(len(teams))
        ok, msg, total = validate_lineup(formation, picks,
                                         budget=budget_for(u.referral_count or 0),
                                         max_starters=max_starters, max_subs=max_subs)
        if not ok:
            return jsonify(ok=False, msg=msg), 400
        entry = Entry.query.filter_by(user_id=u.id, league_id=lg.id, matchday_id=md.id).first()
        if not entry:
            entry = Entry(user_id=u.id, league_id=lg.id, matchday_id=md.id, formation=formation)
            db.session.add(entry); db.session.commit()
        entry.formation = formation
        Pick.query.filter_by(entry_id=entry.id).delete()
        for pk in picks:
            db.session.add(Pick(entry_id=entry.id, slot=int(pk["slot"]),
                                role=pk["role"], player_id=int(pk["player_id"])))
        db.session.commit()
        return jsonify(ok=True, msg="Lineup locked in.", total=total,
                       redirect=url_for("dashboard"))

    @app.route("/my-team/<int:league_id>/<int:matchday_id>")
    @login_required
    def my_team(league_id, matchday_id):
        u = current_user()
        lg = League.query.get_or_404(league_id)
        md = Matchday.query.get_or_404(matchday_id)
        if not Membership.query.filter_by(user_id=u.id, league_id=lg.id).first():
            abort(403)
        entry = Entry.query.filter_by(user_id=u.id, league_id=lg.id, matchday_id=md.id).first()
        if not entry:
            return redirect(url_for("play", league_id=league_id, matchday_id=matchday_id))
        picks_data = []
        for pk in entry.picks:
            player = PLAYERS_BY_ID.get(pk.player_id)
            if player:
                picks_data.append({"slot": pk.slot, "role": pk.role, "player": player})
        return render_template("my_team.html", league=lg, matchday=md, entry=entry,
                               picks=picks_data, formation=entry.formation,
                               formations=FORMATIONS, is_own=True, team_username=u.username)

    @app.route("/league/<int:league_id>/team/<int:user_id>/<int:matchday_id>")
    @login_required
    def view_team(league_id, user_id, matchday_id):
        u = current_user()
        lg = League.query.get_or_404(league_id)
        if not Membership.query.filter_by(user_id=u.id, league_id=lg.id).first():
            abort(403)
        if not Membership.query.filter_by(user_id=user_id, league_id=lg.id).first():
            abort(404)
        target = User.query.get_or_404(user_id)
        md = Matchday.query.get_or_404(matchday_id)
        entry = Entry.query.filter_by(user_id=user_id, league_id=lg.id, matchday_id=md.id).first()
        picks_data = []
        if entry:
            for pk in entry.picks:
                player = PLAYERS_BY_ID.get(pk.player_id)
                if player:
                    picks_data.append({"slot": pk.slot, "role": pk.role, "player": player})
        return render_template("my_team.html", league=lg, matchday=md, entry=entry,
                               picks=picks_data,
                               formation=entry.formation if entry else None,
                               formations=FORMATIONS, is_own=(u.id == user_id),
                               team_username=target.username)

    # ---- admin settle ----
    @app.route("/admin/settle", methods=["GET", "POST"])
    @login_required
    def admin_settle():
        u = current_user()
        first = User.query.order_by(User.id).first()
        if not first or u.id != first.id:
            abort(403)
        matchdays = Matchday.query.order_by(Matchday.date).all()
        sel = request.args.get("md", type=int)
        md = Matchday.query.get(sel) if sel else None

        def md_players(m):
            teams = set()
            for fx in m.fixtures:
                teams.add(fx.home_team); teams.add(fx.away_team)
            return players_for_teams(teams)

        if request.method == "POST":
            md = Matchday.query.get(int(request.form["matchday_id"]))
            Result.query.filter_by(matchday_id=md.id).delete()
            for p in md_players(md):
                pid = p["id"]
                g = int(request.form.get(f"g_{pid}", 0) or 0)
                a = int(request.form.get(f"a_{pid}", 0) or 0)
                cs = bool(request.form.get(f"cs_{pid}"))
                y = int(request.form.get(f"y_{pid}", 0) or 0)
                r = int(request.form.get(f"r_{pid}", 0) or 0)
                if g or a or cs or y or r:
                    db.session.add(Result(matchday_id=md.id, player_id=pid, goals=g,
                                          assists=a, clean_sheet=cs, yellows=y, reds=r))
            db.session.commit()
            results = {r.player_id: r for r in Result.query.filter_by(matchday_id=md.id).all()}
            for e in Entry.query.filter_by(matchday_id=md.id).all():
                e.score = score_entry(e.picks, results)
            md.settled = True
            db.session.commit()
            flash(f"Settled {md.label}.", "ok")
            return redirect(url_for("admin_settle"))

        players = md_players(md) if md else []
        return render_template("admin.html", matchdays=matchdays, md=md, players=players)

    @app.route("/admin/auto-settle/<int:matchday_id>", methods=["POST"])
    @login_required
    def admin_auto_settle(matchday_id):
        u = current_user()
        first = User.query.order_by(User.id).first()
        if not first or u.id != first.id:
            abort(403)
        md = Matchday.query.get_or_404(matchday_id)

        def md_players_for_teams(home, away):
            return players_for_teams({home, away})

        errors = []
        merged = {}  # player_id -> stats dict

        for fx in md.fixtures:
            api_stats, err = fetch_fixture_stats(fx.home_team, fx.away_team, md.date)
            if err:
                errors.append(err)
                continue
            fixture_pool = md_players_for_teams(fx.home_team, fx.away_team)
            for player, stats in match_api_to_pool(api_stats, fixture_pool):
                if any([stats["goals"], stats["assists"], stats["yellows"], stats["reds"],
                        stats["clean_sheet"]]):
                    merged[player["id"]] = stats

        if errors and not merged:
            for e in errors:
                flash(e, "error")
            return redirect(url_for("admin_settle", md=matchday_id))

        Result.query.filter_by(matchday_id=md.id).delete()
        for pid, s in merged.items():
            db.session.add(Result(
                matchday_id=md.id, player_id=pid,
                goals=s["goals"], assists=s["assists"], clean_sheet=s["clean_sheet"],
                yellows=s["yellows"], reds=s["reds"],
            ))
        db.session.commit()

        results = {r.player_id: r for r in Result.query.filter_by(matchday_id=md.id).all()}
        for e in Entry.query.filter_by(matchday_id=md.id).all():
            e.score = score_entry(e.picks, results)
        md.settled = True
        db.session.commit()

        msg = f"Auto-settled {md.label} — {len(merged)} players with stats."
        if errors:
            msg += f" ({len(errors)} fixture(s) had errors: {'; '.join(errors)})"
        flash(msg, "ok")
        return redirect(url_for("admin_settle"))

    # ---- schedule ----
    @app.route("/schedule")
    def schedule():
        matchdays = Matchday.query.order_by(Matchday.date).all()
        return render_template("schedule.html", matchdays=matchdays)

    return app
