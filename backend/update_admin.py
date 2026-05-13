import psycopg2
from app.core.config import settings

conn = psycopg2.connect(settings.DATABASE_URL)
cur = conn.cursor()

new_hash = "$2b$12$ybucCaoRYQrtK1edfVZQGuxuqoLdc1d68Joxy7cDMBOBlBlcTfWDS"
cur.execute("UPDATE usuarios SET password_hash = %s WHERE email = 'admin@foodstore.com'", (new_hash,))
conn.commit()
print('Password updated')
conn.close()