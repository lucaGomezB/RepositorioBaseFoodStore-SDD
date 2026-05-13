# Seed data for initial database population
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.security import hash_password
from app.models.rol import Rol
from app.models.estado_pedido import EstadoPedido
from app.models.forma_pago import FormaPago
from app.models.usuario import Usuario


# Create engine and session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed_roles(session):
    """Seed roles with stable IDs."""
    roles_data = [
        {"id": 1, "nombre": "ADMIN", "descripcion": "Administrador del sistema"},
        {"id": 2, "nombre": "STOCK", "descripcion": "Gestión de inventario"},
        {"id": 3, "nombre": "PEDIDOS", "descripcion": "Gestión de pedidos"},
        {"id": 4, "nombre": "CLIENT", "descripcion": "Cliente del e-commerce"},
    ]

    for rol_data in roles_data:
        existing = session.get(Rol, rol_data["id"])
        if not existing:
            rol = Rol(**rol_data)
            session.add(rol)
    session.commit()
    print("[OK] Roles seeded")


def seed_estados_pedido(session):
    """Seed order states with semantic codes (v5 PK change)."""
    estados_data = [
        {"codigo": "PENDIENTE", "nombre": "Pendiente", "descripcion": "Pedido pendiente de confirmación", "orden": 1, "es_terminal": False},
        {"codigo": "CONFIRMADO", "nombre": "Confirmado", "descripcion": "Pedido confirmado", "orden": 2, "es_terminal": False},
        {"codigo": "EN_PREP", "nombre": "En Preparación", "descripcion": "Pedido en preparación", "orden": 3, "es_terminal": False},
        {"codigo": "EN_CAMINO", "nombre": "En Camino", "descripcion": "Pedido en camino al cliente", "orden": 4, "es_terminal": False},
        {"codigo": "ENTREGADO", "nombre": "Entregado", "descripcion": "Pedido entregado", "orden": 5, "es_terminal": True},
        {"codigo": "CANCELADO", "nombre": "Cancelado", "descripcion": "Pedido cancelado", "orden": 6, "es_terminal": True},
    ]

    for estado_data in estados_data:
        existing = session.get(EstadoPedido, estado_data["codigo"])
        if not existing:
            estado = EstadoPedido(**estado_data)
            session.add(estado)
    session.commit()
    print("[OK] EstadoPedido seeded")


def seed_formas_pago(session):
    """Seed payment methods with stable IDs."""
    formas_data = [
        {"id": 1, "nombre": "EFECTIVO", "descripcion": "Pago en efectivo"},
        {"id": 2, "nombre": "MERCADO_PAGO", "descripcion": "Pago via MercadoPago"},
        {"id": 3, "nombre": "TRANSFERENCIA", "descripcion": "Transferencia bancaria"},
    ]

    for forma_data in formas_data:
        existing = session.get(FormaPago, forma_data["id"])
        if not existing:
            forma = FormaPago(**forma_data)
            session.add(forma)
    session.commit()
    print("[OK] FormaPago seeded")


def seed_admin_user(session):
    """Seed admin user."""
    # Get admin password from env or use default
    admin_password = "admin123"
    password_hash = hash_password(admin_password)

    # Check if admin exists
    existing = session.query(Usuario).filter(Usuario.email == "admin@foodstore.com").first()
    if not existing:
        now = datetime.now().isoformat()
        admin = Usuario(
            email="admin@foodstore.com",
            password_hash=password_hash,
            nombre="Admin",
            apellido="FoodStore",
            rol_id=1,  # ADMIN
            activo=True,
            fecha_creacion=now,
            fecha_actualizacion=now,
        )
        session.add(admin)
        session.commit()
        print("[OK] Admin user seeded")
    else:
        print("[OK] Admin user already exists")


def main():
    """Run all seed functions."""
    print("Starting seed...")

    session = SessionLocal()
    try:
        seed_roles(session)
        seed_estados_pedido(session)
        seed_formas_pago(session)
        seed_admin_user(session)
        print("\n[OK] All seed data populated successfully!")
    except Exception as e:
        print(f"\n✗ Error during seed: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
