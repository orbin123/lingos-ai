import sqlite3
import json

conn = sqlite3.connect("backend/app.db")
c = conn.cursor()

# Get the latest scorecard
c.execute("SELECT session_id, activities FROM session_scorecards ORDER BY id DESC LIMIT 1")
row = c.fetchone()
if row:
    session_id, activities_json = row
    print("Session ID:", session_id)
    activities = json.loads(activities_json)
    for act in activities:
        print(act["archetype_id"], act["raw_score"])

# Also check activity_evaluations
print("\nEvaluations:")
c.execute("""
SELECT a.sequence, a.archetype_id, e.raw_score, e.evaluator_notes
FROM activity_attempts a
JOIN activity_evaluations e ON a.id = e.attempt_id
WHERE a.session_id = ?
""", (session_id,))
for row in c.fetchall():
    print(row[0], row[1], row[2])
    print(row[3][:100] if row[3] else None)

