# Admin schemas — Pydantic v2
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuration schemas
# ---------------------------------------------------------------------------


class ConfigRead(BaseModel):
    """Response schema for a single configuration key-value."""
    clave: str
    valor: str
    descripcion: Optional[str] = None
    updated_by: Optional[int] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "clave": "MAX_ITEMS_PER_ORDER",
                "valor": "20",
                "descripcion": "Maximum items allowed per order",
                "updated_by": 1,
                "updated_at": "2024-01-15T10:30:00",
            },
        },
    }


class ConfigUpdateItem(BaseModel):
    """Single item in a configuration update request."""
    clave: str
    valor: str
    model_config = {
        "json_schema_extra": {
            "example": {
                "clave": "MAX_ITEMS_PER_ORDER",
                "valor": "25",
            },
        },
    }


class ConfigUpdateRequest(BaseModel):
    """Request schema for updating multiple configurations."""
    configuraciones: list[ConfigUpdateItem]
    model_config = {
        "json_schema_extra": {
            "example": {
                "configuraciones": [
                    {"clave": "MAX_ITEMS_PER_ORDER", "valor": "25"},
                    {"clave": "DELIVERY_COST", "valor": "5.00"},
                ],
            },
        },
    }


# ---------------------------------------------------------------------------
# Dashboard / Metrics schemas
# ---------------------------------------------------------------------------


class PedidoEstadoCount(BaseModel):
    """Order count grouped by state."""
    codigo: str
    nombre: str
    cantidad: int
    model_config = {
        "json_schema_extra": {
            "example": {
                "codigo": "PENDIENTE",
                "nombre": "Pendiente",
                "cantidad": 15,
            },
        },
    }


class TopProducto(BaseModel):
    """Top-selling product."""
    nombre: str
    cantidad: int
    model_config = {
        "json_schema_extra": {
            "example": {
                "nombre": "Hamburguesa Clasica",
                "cantidad": 120,
            },
        },
    }


class MetricasResumen(BaseModel):
    """Summary KPIs for admin dashboard."""
    total_ventas: float
    pedidos_por_estado: list[PedidoEstadoCount]
    total_usuarios: int
    top_productos: list[TopProducto]
    model_config = {
        "json_schema_extra": {
            "example": {
                "total_ventas": 15234.50,
                "pedidos_por_estado": [
                    {"codigo": "PENDIENTE", "nombre": "Pendiente", "cantidad": 15},
                    {"codigo": "CONFIRMADO", "nombre": "Confirmado", "cantidad": 42},
                    {"codigo": "ENTREGADO", "nombre": "Entregado", "cantidad": 120},
                ],
                "total_usuarios": 85,
                "top_productos": [
                    {"nombre": "Hamburguesa Clasica", "cantidad": 120},
                    {"nombre": "Papas Fritas", "cantidad": 95},
                ],
            },
        },
    }


class VentaPeriodo(BaseModel):
    """Sales aggregated over a time period."""
    periodo: str
    total: float
    model_config = {
        "json_schema_extra": {
            "example": {
                "periodo": "2024-01-15T00:00:00",
                "total": 15234.50,
            },
        },
    }


class ProductoRanking(BaseModel):
    """Product ranking by sales quantity."""
    nombre: str
    cantidad: int
    model_config = {
        "json_schema_extra": {
            "example": {
                "nombre": "Hamburguesa Clasica",
                "cantidad": 120,
            },
        },
    }


class PedidoEstadoDistribucion(BaseModel):
    """Order distribution by state."""
    codigo: str
    nombre: str
    cantidad: int
    model_config = {
        "json_schema_extra": {
            "example": {
                "codigo": "PENDIENTE",
                "nombre": "Pendiente",
                "cantidad": 15,
            },
        },
    }


# ---------------------------------------------------------------------------
# User list pagination schema
# ---------------------------------------------------------------------------


class UsuarioListResponse(BaseModel):
    """Paginated user list response."""
    items: list[dict]
    total: int
    skip: int
    limit: int
    model_config = {
        "json_schema_extra": {
            "example": {
                "items": [
                    {
                        "id": 1,
                        "email": "admin@foodstore.com",
                        "nombre": "Admin",
                        "apellido": "User",
                        "rol_id": 1,
                        "activo": True,
                        "fecha_creacion": "2024-01-15T10:30:00",
                    },
                ],
                "total": 10,
                "skip": 0,
                "limit": 100,
            },
        },
    }


# ---------------------------------------------------------------------------
# Generic message response
# ---------------------------------------------------------------------------


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Operation completed successfully",
            },
        },
    }
