from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.modules.sessions.models import ActivityAttempt
import json

db = SessionLocal()
attempt = db.query(ActivityAttempt).filter_by(session_id=5, sequence=4).first()
if attempt:
    print(json.dumps(attempt.task_content, indent=2))
else:
    print("Attempt not found")
