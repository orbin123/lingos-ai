import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://coach:coachpass@localhost:5433/coach_db"

def main():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Let's find the active daily session and its activity attempts
    result = session.execute(text("""
        SELECT ds.id, ds.user_id, ds.day_id, aa.sequence, aa.status, aa.task_content
        FROM daily_sessions ds
        JOIN activity_attempts aa ON ds.id = aa.session_id
        ORDER BY ds.id DESC, aa.sequence ASC
        LIMIT 10;
    """))
    
    print("Latest 10 attempts:")
    for row in result:
        print(f"Session ID: {row[0]}, Day: {row[2]}, Seq: {row[3]}, Status: {row[4]}")
        print(f"Task Content: {row[5]}")
        print("-" * 50)

if __name__ == "__main__":
    main()
