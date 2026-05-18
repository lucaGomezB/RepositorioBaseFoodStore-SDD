# Producto Schemas
from typing import Optional, List
from pydantic import ConfigDict, field_validator
from sqlmodel import SQLModel


class IngredienteAsignado(SQLModel):
    """Schema for assigning an ingredient to a product."""
    ingrediente_id: int
    es_removible: bool = True
    es_principal: bool = False
    orden: int = 0
    model_config = {
        "json_schema_extra": {
            "example": {
                "ingrediente_id": 1,
                "es_removible": True,
                "es_principal": True,
                "orden": 0,
            },
        },
    }


class CategoriaAsignada(SQLModel):
    """Schema for assigning a category to a product."""
    categoria_id: int
    es_principal: bool = False
    model_config = {
        "json_schema_extra": {
            "example": {
                "categoria_id": 1,
                "es_principal": True,
            },
        },
    }


class ProductoBase(SQLModel):
    """Base schema for Producto.
    Uses float for API serialization; DB stores Decimal for precision (RN-CA04)."""
    nombre: str
    descripcion: Optional[str] = None
    precio_base: float = 0
    imagenes_url: Optional[str] = None
    tiempo_prep_min: int = 0
    stock_cantidad: int = 0
    disponible: bool = True


class ProductoCreate(ProductoBase):
    """Schema for creating a producto."""
    categorias_ids: List[int] = []
    categoria_principal_id: Optional[int] = None
    ingredientes: Optional[List[IngredienteAsignado]] = []
    
    @field_validator('stock_cantidad')
    @classmethod
    def validar_stock(cls, v):
        if v < 0:
            raise ValueError('stock_cantidad no puede ser negativo')
        return v
    
    @field_validator('categorias_ids')
    @classmethod
    def validar_categorias(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Se requiere al menos 1 categoría para crear un producto')
        return v
    
    @field_validator('ingredientes')
    @classmethod
    def validar_ingredientes(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Se requiere al menos 1 ingrediente para crear un producto')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "nombre": "Hamburguesa Clasica",
                "descripcion": "Hamburguesa con lechuga, tomate y cheddar",
                "precio_base": 8.50,
                "imagenes_url": "https://example.com/hamburguesa.jpg",
                "tiempo_prep_min": 15,
                "stock_cantidad": 50,
                "disponible": True,
                "categorias_ids": [1],
                "categoria_principal_id": 1,
                "ingredientes": [
                    {"ingrediente_id": 1, "es_removible": False, "es_principal": True, "orden": 0},
                ],
            },
        },
    }


class ProductoUpdate(SQLModel):
    """Schema for updating a producto."""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio_base: Optional[float] = None
    imagenes_url: Optional[str] = None
    tiempo_prep_min: Optional[int] = None
    stock_cantidad: Optional[int] = None
    disponible: Optional[bool] = None
    categorias_ids: Optional[List[int]] = None
    
    @field_validator('stock_cantidad')
    @classmethod
    def validar_stock(cls, v):
        if v is not None and v < 0:
            raise ValueError('stock_cantidad no puede ser negativo')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "nombre": "Hamburguesa Clasica",
                "precio_base": 9.50,
                "disponible": True,
            },
        },
    }


class ProductoRead(ProductoBase):
    """Schema for reading a producto."""
    id: int
    fecha_creacion: Optional[str] = None
    fecha_actualizacion: Optional[str] = None
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "nombre": "Hamburguesa Clasica",
                "descripcion": "Hamburguesa con lechuga, tomate y cheddar",
                "precio_base": 8.50,
                "imagenes_url": "https://example.com/hamburguesa.jpg",
                "tiempo_prep_min": 15,
                "stock_cantidad": 50,
                "disponible": True,
                "fecha_creacion": "2024-01-15T10:30:00",
            },
        },
    )


class StockUpdate(SQLModel):
    """Schema for atomic stock update."""
    cantidad: int  # positive to increment, negative to decrement
    
    @field_validator('cantidad')
    @classmethod
    def validar_cantidad(cls, v):
        if v == 0:
            raise ValueError('cantidad debe ser distinto de cero')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "cantidad": 10,
            },
        },
    }


class ProductoIngredienteRead(SQLModel):
    """Schema for reading an ingredient relationship."""
    ingrediente_id: int
    ingrediente_nombre: str
    es_removible: bool
    es_principal: bool
    orden: int
    es_alergeno: bool = False
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "ingrediente_id": 1,
                "ingrediente_nombre": "Carne de res",
                "es_removible": False,
                "es_principal": True,
                "orden": 0,
                "es_alergeno": False,
            },
        },
    )


class ProductoCategoriaRead(SQLModel):
    """Schema for reading a category relationship."""
    categoria_id: int
    categoria_nombre: str
    es_principal: bool
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "categoria_id": 1,
                "categoria_nombre": "Hamburguesas",
                "es_principal": True,
            },
        },
    )


class ProductoCatalogoRead(SQLModel):
    """Schema for public catalog product reading.
    
    Excludes internal fields: stock_cantidad, eliminado_en.
    Includes computed hay_stock and relationship data.
    Uses float for API serialization; DB stores Decimal for precision.
    """
    id: int
    nombre: str
    descripcion: Optional[str] = None
    precio_base: float = 0
    imagenes_url: Optional[str] = None
    tiempo_prep_min: int = 0
    disponible: bool = True
    hay_stock: bool
    fecha_creacion: Optional[str] = None
    fecha_actualizacion: Optional[str] = None
    ingredientes: List[ProductoIngredienteRead] = []
    categorias: List[ProductoCategoriaRead] = []
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "nombre": "Hamburguesa Clasica",
                "descripcion": "Hamburguesa con lechuga, tomate y cheddar",
                "precio_base": 8.50,
                "imagenes_url": "https://example.com/hamburguesa.jpg",
                "tiempo_prep_min": 15,
                "disponible": True,
                "hay_stock": True,
                "ingredientes": [
                    {
                        "ingrediente_id": 1,
                        "ingrediente_nombre": "Carne de res",
                        "es_removible": False,
                        "es_principal": True,
                        "orden": 0,
                        "es_alergeno": False,
                    },
                ],
                "categorias": [
                    {
                        "categoria_id": 1,
                        "categoria_nombre": "Hamburguesas",
                        "es_principal": True,
                    },
                ],
            },
        },
    )


class CatalogoResponse(SQLModel):
    """Wrapper for paginated catalog response."""
    items: List[ProductoCatalogoRead]
    total_count: int
