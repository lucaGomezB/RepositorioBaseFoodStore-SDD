import psycopg2
from app.core.config import settings

conn = psycopg2.connect(settings.DATABASE_URL)
cur = conn.cursor()

# Delete all refresh tokens
cur.execute("DELETE FROM refresh_tokens")
conn.commit()
print('All refresh tokens deleted')

conn.close()