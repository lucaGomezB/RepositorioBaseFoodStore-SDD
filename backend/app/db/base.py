# SQLModel base for all models
from sqlmodel import SQLModel


# This is the base class that all models will inherit from
# It provides the metadata that Alembic needs for autogenerate
class Base(SQLModel):
    pass