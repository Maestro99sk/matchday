"""Database models for Matchday (pick-a-5 budget game)."""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Membership(db.Model):
    __tablename__ = "memberships"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey("leagues.id"), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint("user_id", "league_id", name="uq_member"),)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # referrals: each user has a unique code; referred_by points at the referrer's id
    referral_code = db.Column(db.String(10), unique=True, index=True)
    referred_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    referral_count = db.Column(db.Integer, default=0)   # confirmed referrals
    signup_ip = db.Column(db.String(64), nullable=True) # soft anti-farming guard
    memberships = db.relationship("Membership", backref="user", lazy=True)
    entries = db.relationship("Entry", backref="user", lazy=True)

    def set_password(self, pw): self.password_hash = generate_password_hash(pw, method="pbkdf2:sha256")
    def check_password(self, pw): return check_password_hash(self.password_hash, pw)


class League(db.Model):
    __tablename__ = "leagues"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    code = db.Column(db.String(8), unique=True, nullable=False, index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    memberships = db.relationship("Membership", backref="league", lazy=True)
    entries = db.relationship("Entry", backref="league", lazy=True)


class Matchday(db.Model):
    __tablename__ = "matchdays"
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(64), nullable=False)
    date = db.Column(db.Date, nullable=False)
    lock_time = db.Column(db.DateTime, nullable=False)
    settled = db.Column(db.Boolean, default=False)
    fixtures = db.relationship("Fixture", backref="matchday", lazy=True)


class Fixture(db.Model):
    __tablename__ = "fixtures"
    id = db.Column(db.Integer, primary_key=True)
    matchday_id = db.Column(db.Integer, db.ForeignKey("matchdays.id"), nullable=False)
    home_team = db.Column(db.String(48), nullable=False)
    away_team = db.Column(db.String(48), nullable=False)


# Players live in players.json (static reference data), not the DB.
# Results reference players by their json id.
class Result(db.Model):
    __tablename__ = "results"
    id = db.Column(db.Integer, primary_key=True)
    matchday_id = db.Column(db.Integer, db.ForeignKey("matchdays.id"), nullable=False)
    player_id = db.Column(db.Integer, nullable=False)   # -> players.json id
    goals = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    clean_sheet = db.Column(db.Boolean, default=False)
    yellows = db.Column(db.Integer, default=0)
    reds = db.Column(db.Integer, default=0)
    played = db.Column(db.Boolean, default=True)  # False = DNP, triggers same-nation auto-sub
    __table_args__ = (db.UniqueConstraint("matchday_id", "player_id", name="uq_result"),)


class Entry(db.Model):
    __tablename__ = "entries"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey("leagues.id"), nullable=False)
    matchday_id = db.Column(db.Integer, db.ForeignKey("matchdays.id"), nullable=False)
    formation = db.Column(db.String(8), nullable=False)
    score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    picks = db.relationship("Pick", backref="entry", lazy=True, cascade="all, delete-orphan")
    __table_args__ = (db.UniqueConstraint("user_id", "league_id", "matchday_id", name="uq_entry"),)


class Pick(db.Model):
    __tablename__ = "picks"
    id = db.Column(db.Integer, primary_key=True)
    entry_id = db.Column(db.Integer, db.ForeignKey("entries.id"), nullable=False)
    slot = db.Column(db.Integer, nullable=False)        # 0..4 index in formation
    role = db.Column(db.String(4), nullable=False)      # GK/DEF/MID/FWD
    player_id = db.Column(db.Integer, nullable=False)   # -> players.json id
