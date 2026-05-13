from app.core.database import SessionLocal
from app.models.usuario import Usuario
from sqlmodel import select

session = SessionLocal()
statement = select(Usuario).where(Usuario.email == "admin@foodstore.com")
user = session.exec(statement).first()
print('User:', user)
if user:
    print('Email:', user.email)
    print('Password hash:', user.password_hash)
session.close()