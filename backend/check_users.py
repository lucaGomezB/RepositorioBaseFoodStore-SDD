import psycopg2
from app.core.config import settings

conn = psycopg2.connect(settings.DATABASE_URL)
cur = conn.cursor()

cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'usuarios'")
cols = cur.fetchall()
print('Columns in usuarios:', [c[0] for c in cols])

# Also check the admin user
cur.execute("SELECT id, email, nombre FROM usuarios WHERE email = 'admin@foodstore.com'")
admin = cur.fetchone()
print('Admin user:', admin)

conn.close()