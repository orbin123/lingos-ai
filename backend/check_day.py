import asyncio
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.modules.preferences.service import PreferenceService

db = SessionLocal()
pref = PreferenceService(db).get(user_id=1)
print(f"User 1 - Week {pref.current_week} Day {pref.current_day_in_week}")
