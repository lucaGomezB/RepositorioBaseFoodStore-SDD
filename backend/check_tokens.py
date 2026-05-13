import psycopg2
from app.core.config import settings

conn = psycopg2.connect(settings.DATABASE_URL)
cur = conn.cursor()

# Check refresh tokens
cur.execute("SELECT id, user_id, revoked, created_at FROM refresh_tokens ORDER BY created_at DESC LIMIT 5")
tokens = cur.fetchall()
print('Recent refresh tokens:')
for t in tokens:
    print(f'  ID: {t[0]}, User: {t[1]}, Revoked: {t[2]}, Created: {t[3]}')

conn.close()