from sqlalchemy import text
from app.core.database import SessionLocal

db = SessionLocal()
db.execute(text("DELETE FROM daily_sessions WHERE user_id = 1 AND day_id = 'day_24_01_02'"))
db.commit()
print("Done.")
