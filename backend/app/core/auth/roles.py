# Role enum for the food store backend
from enum import IntEnum


class Role(IntEnum):
    """
    Role identifiers matching seed data and DB roles table.
    
    Values:
        ADMIN (1): Full system access
        STOCK (2): Inventory management
        PEDIDOS (3): Order management
        CLIENT (4): Regular customer
        COCINA (5): Kitchen operator — KDS display, limited FSM transitions
    """
    ADMIN = 1
    STOCK = 2
    PEDIDOS = 3
    CLIENT = 4
    COCINA = 5
