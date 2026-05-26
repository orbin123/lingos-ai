from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.modules.sessions.models import DailySession, ActivityAttempt

db = SessionLocal()
sessions = db.query(DailySession).filter_by(user_id=1, day_id="day_24w_01_02").all()
for s in sessions:
    print(f"Session {s.session_id} - status: {s.status}")
    for a in s.attempts:
        print(f"  Attempt {a.sequence} - archetype: {a.archetype_id}")
