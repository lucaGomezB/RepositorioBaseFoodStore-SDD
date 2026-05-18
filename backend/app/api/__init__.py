# API router configuration
from fastapi import APIRouter

# Create main API router
router = APIRouter()

# Import and include sub-routers
from app.api.auth import router as auth_router
from app.api.productos import router as productos_router
from app.api.categorias import router as categorias_router
from app.api.ingredientes import router as ingredientes_router
from app.api.catalogo import router as catalogo_router
from app.api.direcciones import router as direcciones_router
from app.api.perfil import router as perfil_router
from app.api.pedidos import router as pedidos_router
from app.api.pagos import router as pagos_router
from app.api.admin import (
    dashboard_router,
    orders_router,
    users_router,
    stock_router,
    config_router,
)

router.include_router(auth_router)
router.include_router(productos_router)
router.include_router(categorias_router)
router.include_router(ingredientes_router)
router.include_router(catalogo_router)
router.include_router(direcciones_router)
router.include_router(perfil_router)
router.include_router(pedidos_router)
router.include_router(pagos_router)
router.include_router(dashboard_router)
router.include_router(orders_router)
router.include_router(users_router)
router.include_router(stock_router)
router.include_router(config_router)


@router.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint for API v1."""
    return {"status": "ok", "service": "food-store-api-v1"}


@router.get("/", tags=["Root"])
def api_root():
    """API root endpoint."""
    return {"message": "Food Store API v1", "docs": "/docs"}