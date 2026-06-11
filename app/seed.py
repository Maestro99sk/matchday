"""Create schema and load real World Cup fixtures. Run: python -m app.seed"""
from . import create_app
from .models import db, Matchday, Fixture, Entry, Pick, Result
from .config import MATCHDAYS


def run():
    app = create_app()
    with app.app_context():
        db.create_all()
        # Migrate: add played column to results if missing (SQLite safe)
        try:
            db.session.execute(db.text(
                "ALTER TABLE results ADD COLUMN played BOOLEAN DEFAULT 1"
            ))
            db.session.commit()
            print("Migrated: added results.played column.")
        except Exception:
            pass  # column already exists
        # Clear everything except users and leagues
        Pick.query.delete()
        Entry.query.delete()
        Result.query.delete()
        Fixture.query.delete()
        Matchday.query.delete()
        db.session.commit()

        for md in MATCHDAYS:
            m = Matchday(label=md["label"], date=md["date"], lock_time=md["lock"], settled=False)
            db.session.add(m); db.session.commit()
            for home, away in md["fixtures"]:
                db.session.add(Fixture(matchday_id=m.id, home_team=home, away_team=away))
        db.session.commit()
        print(f"Seeded {Matchday.query.count()} matchdays, {Fixture.query.count()} fixtures.")


if __name__ == "__main__":
    run()
