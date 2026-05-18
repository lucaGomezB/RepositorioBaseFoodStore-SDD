"""merge_heads

Revision ID: 1702ad949a80
Revises: e2f3b4c5d6e7, f1a2b3c4d5e6
Create Date: 2026-05-13 08:36:05.057188

"""
from typing import Sequence, Union



# revision identifiers, used by Alembic.
revision: str = '1702ad949a80'
down_revision: Union[str, Sequence[str], None] = ('e2f3b4c5d6e7', 'f1a2b3c4d5e6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
