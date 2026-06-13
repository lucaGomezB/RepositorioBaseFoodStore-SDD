# Usuarios de Prueba

## Seed inicial

Ejecutar `python -m app.db.seed` desde `backend/` para poblar la base de datos con los usuarios iniciales.

### Usuarios

| Email | Contrasena | Rol | Descripcion |
|-------|-----------|-----|-------------|
| `admin@foodstore.com` | `admin123` | ADMIN (1) | Acceso completo al sistema: CRUD de usuarios, metricas, configuracion, todas las pantallas |
| `cocina@foodstore.com` | `cocina123` | COCINA (5) | Acceso a la pantalla de cocina (KDS) para gestion de pedidos en preparacion |

> **Nota**: Las contrasenas se hashean con bcrypt (cost factor 12) al ejecutar el seed. No es necesario hashearlas manualmente.

### Datos de referencia creados por el seed

Ademas de los usuarios, el seed crea:
- **Roles** (5): ADMIN, STOCK, PEDIDOS, CLIENT, COCINA
- **Estados de pedido** (6): PENDIENTE, CONFIRMADO, EN_PREPARACION, EN_CAMINO, ENTREGADO, CANCELADO
- **Formas de pago** (3): EFECTIVO, MERCADO_PAGO, TRANSFERENCIA
- **Configuraciones del sistema**: costo de envio, horarios, tiempo estimado de entrega, contacto

---

## Datos de prueba (catalogo)

Ejecutar `python -m app.db.sample_data` desde `backend/` para poblar el catalogo de productos.

### Categorias

| Nombre | Subcategorias |
|--------|--------------|
| Hamburguesas | Clasicas, Premium |
| Pizzas | Muzzarella, Especiales |
| Bebidas | Gaseosas, Aguas |
| Postres | (sin subcategorias) |

### Productos

| Producto | Precio | Stock | Tiempo preparacion |
|----------|--------|-------|-------------------|
| Hamburguesa Clasica | $8.50 | 50 | 10 min |
| Hamburguesa Premium | $12.00 | 30 | 15 min |
| Hamburguesa de Pollo | $9.50 | 40 | 12 min |
| Pizza Muzzarella | $10.00 | 25 | 20 min |
| Pizza Especial | $14.00 | 20 | 25 min |
| Coca-Cola 500ml | $2.50 | 100 | - |
| Sprite 500ml | $2.50 | 100 | - |
| Agua Mineral 500ml | $1.50 | 80 | - |
| Papas Fritas | $4.50 | 60 | 8 min |
| Flan con Crema | $5.00 | 35 | 5 min |

---

## Roles del sistema

| ID | Rol | Descripcion |
|----|-----|-------------|
| 1 | ADMIN | Administrador del sistema |
| 2 | STOCK | Gestion de inventario |
| 3 | PEDIDOS | Gestion de pedidos |
| 4 | CLIENT | Cliente del e-commerce |
| 5 | COCINA | Operacion de cocina |

---

## Comandos utiles

```bash
# Seed inicial (roles, usuarios, configuracion)
cd backend
python -m app.db.seed

# Datos de muestra (catalogo, productos, ingredientes)
python -m app.db.sample_data

# Verificar migraciones
alembic current

# Aplicar migraciones pendientes
alembic upgrade head
```

> **Importante**: Ejecutar `alembic upgrade head` antes del seed para asegurar que las tablas existen.
