from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.modules.sessions.models import DailySession, ActivityAttempt
import json

db = SessionLocal()
sessions = db.query(DailySession).filter_by(user_id=1).all()
for s in sessions:
    print(f"Session {s.session_id} - status: {s.status} - day_id: {s.day_id}")
    for a in s.attempts:
        content = a.task_content or {}
        topic = content.get('topic') or content.get('topic_override') or 'none'
        print(f"  Attempt {a.sequence} - {a.archetype_id} - topic: {topic}")
