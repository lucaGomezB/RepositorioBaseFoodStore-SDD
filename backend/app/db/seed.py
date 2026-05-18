# Seed data for initial database population
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.security import hash_password
from app.models.rol import Rol
from app.models.estado_pedido import EstadoPedido
from app.models.forma_pago import FormaPago
from app.models.usuario import Usuario
from app.models.configuracion import Configuracion
from app.models.usuario_rol import UsuarioRol


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
    print("[OK] Roles ready")


def seed_estados_pedido(session):
    """Seed order states with semantic codes (v5 PK change)."""
    estados_data = [
        {"codigo": "PENDIENTE", "nombre": "Pendiente", "descripcion": "Pedido pendiente de confirmación", "orden": 1, "es_terminal": False},
        {"codigo": "CONFIRMADO", "nombre": "Confirmado", "descripcion": "Pedido confirmado", "orden": 2, "es_terminal": False},
        {"codigo": "EN_PREPARACION", "nombre": "En Preparación", "descripcion": "Pedido en preparación", "orden": 3, "es_terminal": False},
        {"codigo": "EN_CAMINO", "nombre": "En Camino", "descripcion": "Pedido en camino al cliente", "orden": 4, "es_terminal": False},
        {"codigo": "ENTREGADO", "nombre": "Entregado", "descripcion": "Pedido entregado", "orden": 5, "es_terminal": True},
        {"codigo": "CANCELADO", "nombre": "Cancelado", "descripcion": "Pedido cancelado", "orden": 6, "es_terminal": True},
    ]

    for estado_data in estados_data:
        existing = session.get(EstadoPedido, estado_data["codigo"])
        if not existing:
            estado = EstadoPedido(**estado_data)
            session.add(estado)
    print("[OK] EstadoPedido ready")


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
    print("[OK] FormaPago ready")


def seed_admin_user(session):
    """Seed admin user."""
    admin_password = settings.ADMIN_PASSWORD if hasattr(settings, 'ADMIN_PASSWORD') else "admin123"
    password_hash = hash_password(admin_password)

    existing = session.query(Usuario).filter(Usuario.email == "admin@foodstore.com").first()
    if not existing:
        now = datetime.now().isoformat()
        admin = Usuario(
            email="admin@foodstore.com",
            password_hash=password_hash,
            nombre="Admin",
            apellido="FoodStore",
            activo=True,
            fecha_creacion=now,
            fecha_actualizacion=now,
        )
        session.add(admin)
        session.flush()  # Flush to get admin.id

        admin_rol = UsuarioRol(usuario_id=admin.id, rol_id=1)
        session.add(admin_rol)
        print("[OK] Admin user ready")
    else:
        # Ensure existing admin has ADMIN role in UsuarioRol
        existing_rol = session.query(UsuarioRol).filter(
            UsuarioRol.usuario_id == existing.id,
            UsuarioRol.rol_id == 1,
        ).first()
        if not existing_rol:
            admin_rol = UsuarioRol(usuario_id=existing.id, rol_id=1)
            session.add(admin_rol)
        print("[OK] Admin user already exists")


def seed_configuraciones(session):
    """Seed default system configurations."""
    configs_data = [
        {"clave": "costo_envio", "valor": "50.00", "descripcion": "Costo fijo de envío"},
        {"clave": "horario_apertura", "valor": "09:00", "descripcion": "Horario de apertura (HH:MM)"},
        {"clave": "horario_cierre", "valor": "22:00", "descripcion": "Horario de cierre (HH:MM)"},
        {"clave": "tiempo_estimado_entrega_min", "valor": "30", "descripcion": "Tiempo estimado de entrega en minutos"},
        {"clave": "telefono_contacto", "valor": "", "descripcion": "Teléfono de contacto del local"},
        {"clave": "direccion_local", "valor": "", "descripcion": "Dirección del local"},
    ]

    for cfg in configs_data:
        existing = session.get(Configuracion, cfg["clave"])
        if not existing:
            config = Configuracion(
                clave=cfg["clave"],
                valor=cfg["valor"],
                descripcion=cfg["descripcion"],
                updated_at=datetime.now(timezone.utc),
            )
            session.add(config)
    print("[OK] Configuraciones ready")


def main():
    """Run all seed functions."""
    print("Starting seed...")

    session = SessionLocal()
    try:
        seed_roles(session)
        seed_estados_pedido(session)
        seed_formas_pago(session)
        seed_admin_user(session)
        seed_configuraciones(session)
        session.commit()
        print("\n[OK] All seed data populated successfully!")
    except Exception as e:
        print(f"\n✗ Error during seed: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
