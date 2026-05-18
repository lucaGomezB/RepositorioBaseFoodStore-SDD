# Sample data for Food Store
# Products, categories, ingredients and their relationships
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.categoria import Categoria
from app.models.producto import Producto
from app.models.ingrediente import Ingrediente
from app.models.producto_categoria import ProductoCategoria
from app.models.producto_ingrediente import ProductoIngrediente


# Create engine and session (same session pattern as seed.py)
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed_categorias(session):
    """Seed hierarchical categories with stable IDs."""
    now = datetime.now(timezone.utc).isoformat()
    categorias_data = [
        # Root categories
        {"id": 1, "nombre": "Hamburguesas", "descripcion": "Hamburguesas de todo tipo", "parent_id": None, "orden_display": 1},
        {"id": 2, "nombre": "Clasicas", "descripcion": "Hamburguesas clasicas", "parent_id": 1, "orden_display": 1},
        {"id": 3, "nombre": "Premium", "descripcion": "Hamburguesas premium", "parent_id": 1, "orden_display": 2},
        {"id": 4, "nombre": "Pizzas", "descripcion": "Pizzas de todo tipo", "parent_id": None, "orden_display": 2},
        {"id": 5, "nombre": "Muzzarella", "descripcion": "Pizzas de muzzarella", "parent_id": 4, "orden_display": 1},
        {"id": 6, "nombre": "Especiales", "descripcion": "Pizzas especiales", "parent_id": 4, "orden_display": 2},
        {"id": 7, "nombre": "Bebidas", "descripcion": "Bebidas de todo tipo", "parent_id": None, "orden_display": 3},
        {"id": 8, "nombre": "Gaseosas", "descripcion": "Gaseosas", "parent_id": 7, "orden_display": 1},
        {"id": 9, "nombre": "Aguas", "descripcion": "Agua mineral y aguas saborizadas", "parent_id": 7, "orden_display": 2},
        {"id": 10, "nombre": "Postres", "descripcion": "Postres y dulces", "parent_id": None, "orden_display": 4},
    ]

    count = 0
    for cat_data in categorias_data:
        existing = session.get(Categoria, cat_data["id"])
        if not existing:
            categoria = Categoria(
                **cat_data,
                fecha_creacion=now,
                fecha_actualizacion=now,
            )
            session.add(categoria)
            count += 1
    session.commit()
    if count > 0:
        print(f"[OK] Created {count} categories")
    else:
        print("[OK] Categories already exist")


def seed_ingredientes(session):
    """Seed ingredients with allergen flags using stable IDs."""
    now = datetime.now(timezone.utc).isoformat()
    ingredientes_data = [
        {"id": 1, "nombre": "Harina de Trigo", "descripcion": "Harina de trigo refinada", "es_alergeno": True},
        {"id": 2, "nombre": "Lactosa", "descripcion": "Lactosa (presente en productos lacteos)", "es_alergeno": True},
        {"id": 3, "nombre": "Huevo", "descripcion": "Huevo fresco", "es_alergeno": True},
        {"id": 4, "nombre": "Soja", "descripcion": "Soja y derivados", "es_alergeno": True},
        {"id": 5, "nombre": "Carne Vacuna", "descripcion": "Carne de res molida", "es_alergeno": False},
        {"id": 6, "nombre": "Pollo", "descripcion": "Pechuga de pollo", "es_alergeno": False},
        {"id": 7, "nombre": "Queso Muzzarella", "descripcion": "Queso muzzarella (contiene lactosa)", "es_alergeno": False},
        {"id": 8, "nombre": "Tomate", "descripcion": "Tomate fresco", "es_alergeno": False},
        {"id": 9, "nombre": "Lechuga", "descripcion": "Lechuga criolla", "es_alergeno": False},
        {"id": 10, "nombre": "Cebolla", "descripcion": "Cebolla morada", "es_alergeno": False},
        {"id": 11, "nombre": "Pan de Hamburguesa", "descripcion": "Pan de hamburguesa (contiene harina de trigo y huevo)", "es_alergeno": False},
        {"id": 12, "nombre": "Papa", "descripcion": "Papa blanca", "es_alergeno": False},
    ]

    count = 0
    for ing_data in ingredientes_data:
        existing = session.get(Ingrediente, ing_data["id"])
        if not existing:
            ingrediente = Ingrediente(
                **ing_data,
                fecha_creacion=now,
                fecha_actualizacion=now,
            )
            session.add(ingrediente)
            count += 1
    session.commit()
    if count > 0:
        print(f"[OK] Created {count} ingredients")
    else:
        print("[OK] Ingredients already exist")


def seed_productos(session):
    """Seed products with stable IDs."""
    now = datetime.now(timezone.utc).isoformat()
    productos_data = [
        {
            "id": 1,
            "nombre": "Hamburguesa Clasica",
            "descripcion": "Hamburguesa clasica con carne, lechuga, tomate y cebolla",
            "precio_base": Decimal("8.50"),
            "stock_cantidad": 50,
            "tiempo_prep_min": 10,
            "disponible": True,
        },
        {
            "id": 2,
            "nombre": "Hamburguesa Premium",
            "descripcion": "Hamburguesa premium con queso muzzarella",
            "precio_base": Decimal("12.00"),
            "stock_cantidad": 30,
            "tiempo_prep_min": 15,
            "disponible": True,
        },
        {
            "id": 3,
            "nombre": "Hamburguesa de Pollo",
            "descripcion": "Hamburguesa de pollo con lechuga y tomate",
            "precio_base": Decimal("9.50"),
            "stock_cantidad": 40,
            "tiempo_prep_min": 12,
            "disponible": True,
        },
        {
            "id": 4,
            "nombre": "Pizza Muzzarella",
            "descripcion": "Pizza de muzzarella clasica",
            "precio_base": Decimal("10.00"),
            "stock_cantidad": 25,
            "tiempo_prep_min": 20,
            "disponible": True,
        },
        {
            "id": 5,
            "nombre": "Pizza Especial",
            "descripcion": "Pizza especial con cebolla",
            "precio_base": Decimal("14.00"),
            "stock_cantidad": 20,
            "tiempo_prep_min": 25,
            "disponible": True,
        },
        {
            "id": 6,
            "nombre": "Coca-Cola 500ml",
            "descripcion": "Coca-Cola clasica 500ml",
            "precio_base": Decimal("2.50"),
            "stock_cantidad": 100,
            "tiempo_prep_min": 0,
            "disponible": True,
        },
        {
            "id": 7,
            "nombre": "Sprite 500ml",
            "descripcion": "Sprite 500ml",
            "precio_base": Decimal("2.50"),
            "stock_cantidad": 100,
            "tiempo_prep_min": 0,
            "disponible": True,
        },
        {
            "id": 8,
            "nombre": "Agua Mineral 500ml",
            "descripcion": "Agua mineral sin gas 500ml",
            "precio_base": Decimal("1.50"),
            "stock_cantidad": 80,
            "tiempo_prep_min": 0,
            "disponible": True,
        },
        {
            "id": 9,
            "nombre": "Papas Fritas",
            "descripcion": "Papas fritas clasicas",
            "precio_base": Decimal("4.50"),
            "stock_cantidad": 60,
            "tiempo_prep_min": 8,
            "disponible": True,
        },
        {
            "id": 10,
            "nombre": "Flan con Crema",
            "descripcion": "Flan casero con crema",
            "precio_base": Decimal("5.00"),
            "stock_cantidad": 35,
            "tiempo_prep_min": 5,
            "disponible": True,
        },
    ]

    count = 0
    for prod_data in productos_data:
        existing = session.get(Producto, prod_data["id"])
        if not existing:
            producto = Producto(
                **prod_data,
                fecha_creacion=now,
                fecha_actualizacion=now,
            )
            session.add(producto)
            count += 1
    session.commit()
    if count > 0:
        print(f"[OK] Created {count} products")
    else:
        print("[OK] Products already exist")


def seed_producto_categorias(session):
    """Link products to their categories (many-to-many)."""
    datetime.now(timezone.utc).isoformat()
    # (producto_id, categoria_id, es_principal)
    relaciones = [
        # Hamburguesas
        (1, 2, True),   # Hamburguesa Clasica -> Clasicas
        (2, 3, True),   # Hamburguesa Premium -> Premium
        (3, 2, True),   # Hamburguesa de Pollo -> Clasicas
        # Pizzas
        (4, 5, True),   # Pizza Muzzarella -> Muzzarella
        (5, 6, True),   # Pizza Especial -> Especiales
        # Bebidas
        (6, 8, True),   # Coca-Cola -> Gaseosas
        (7, 8, True),   # Sprite -> Gaseosas
        (8, 9, True),   # Agua Mineral -> Aguas
        # Papas Fritas -> Clasicas (Hamburguesas)
        (9, 2, True),   # Papas Fritas -> Clasicas
        # Postres
        (10, 10, True), # Flan con Crema -> Postres
    ]

    count = 0
    for prod_id, cat_id, principal in relaciones:
        # Check if this relationship already exists via the unique constraint
        existing = session.query(ProductoCategoria).filter(
            ProductoCategoria.producto_id == prod_id,
            ProductoCategoria.categoria_id == cat_id,
        ).first()
        if not existing:
            relacion = ProductoCategoria(
                producto_id=prod_id,
                categoria_id=cat_id,
                es_principal=principal,
            )
            session.add(relacion)
            count += 1
    session.commit()
    if count > 0:
        print(f"[OK] Linked {count} product-category relationships")
    else:
        print("[OK] Product-category links already exist")


def seed_producto_ingredientes(session):
    """Link products to their ingredients (many-to-many)."""
    # (producto_id, ingrediente_id, es_removible, es_principal, orden)
    relaciones = [
        # Hamburguesa Clasica (id=1): Carne, Pan, Lechuga, Tomate, Cebolla
        (1, 5, False, True, 1),   # Carne Vacuna - principal, no removible
        (1, 11, False, True, 2),  # Pan - principal, no removible
        (1, 9, True, False, 3),   # Lechuga - removible
        (1, 8, True, False, 4),   # Tomate - removible
        (1, 10, True, False, 5),  # Cebolla - removible
        # Hamburguesa Premium (id=2): Carne, Pan, Queso, Lechuga, Tomate
        (2, 5, False, True, 1),   # Carne Vacuna - principal
        (2, 11, False, True, 2),  # Pan - principal
        (2, 7, True, False, 3),   # Queso Muzzarella - removible
        (2, 9, True, False, 4),   # Lechuga - removible
        (2, 8, True, False, 5),   # Tomate - removible
        # Hamburguesa de Pollo (id=3): Pollo, Pan, Lechuga, Tomate
        (3, 6, False, True, 1),   # Pollo - principal
        (3, 11, False, True, 2),  # Pan - principal
        (3, 9, True, False, 3),   # Lechuga - removible
        (3, 8, True, False, 4),   # Tomate - removible
        # Pizza Muzzarella (id=4): Harina, Queso, Tomate
        (4, 1, False, True, 1),   # Harina de Trigo - principal
        (4, 7, False, True, 2),   # Queso Muzzarella - principal
        (4, 8, False, False, 3),  # Tomate - no removible (salsa)
        # Pizza Especial (id=5): Harina, Queso, Tomate, Cebolla
        (5, 1, False, True, 1),   # Harina de Trigo - principal
        (5, 7, False, True, 2),   # Queso Muzzarella - principal
        (5, 8, False, False, 3),  # Tomate - no removible (salsa)
        (5, 10, True, False, 4),  # Cebolla - removible
        # Coca-Cola 500ml (id=6): sin ingredientes
        # Sprite 500ml (id=7): sin ingredientes
        # Agua Mineral 500ml (id=8): sin ingredientes
        # Papas Fritas (id=9): Papa
        (9, 12, False, True, 1),  # Papa - principal
        # Flan con Crema (id=10): Lactosa, Huevo
        (10, 2, False, True, 1),  # Lactosa - principal
        (10, 3, False, True, 2),  # Huevo - principal
    ]

    count = 0
    for prod_id, ing_id, removible, principal, orden in relaciones:
        existing = session.query(ProductoIngrediente).filter(
            ProductoIngrediente.producto_id == prod_id,
            ProductoIngrediente.ingrediente_id == ing_id,
        ).first()
        if not existing:
            relacion = ProductoIngrediente(
                producto_id=prod_id,
                ingrediente_id=ing_id,
                es_removible=removible,
                es_principal=principal,
                orden=orden,
            )
            session.add(relacion)
            count += 1
    session.commit()
    if count > 0:
        print(f"[OK] Linked {count} product-ingredient relationships")
    else:
        print("[OK] Product-ingredient links already exist")


def main():
    """Run all seed functions for sample data."""
    print("Seeding sample data...")

    session = SessionLocal()
    try:
        seed_categorias(session)
        seed_ingredientes(session)
        seed_productos(session)
        seed_producto_categorias(session)
        seed_producto_ingredientes(session)
        print("\n[OK] All sample data populated successfully!")
    except Exception as e:
        print(f"\n✗ Error during sample data seeding: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
