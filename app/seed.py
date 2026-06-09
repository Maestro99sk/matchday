"""Create schema and load real World Cup fixtures. Run: python -m app.seed"""
from . import create_app
from .models import db, Matchday, Fixture
from .config import MATCHDAYS


def run():
    app = create_app()
    with app.app_context():
        db.drop_all(); db.create_all()
        for md in MATCHDAYS:
            m = Matchday(label=md["label"], date=md["date"], lock_time=md["lock"], settled=False)
            db.session.add(m); db.session.commit()
            for home, away in md["fixtures"]:
                db.session.add(Fixture(matchday_id=m.id, home_team=home, away_team=away))
            db.session.commit()
        print(f"Seeded {Matchday.query.count()} matchdays, {Fixture.query.count()} fixtures.")
        print("Players load from players.json (1,264). Run: python run.py")


if __name__ == "__main__":
    run()
