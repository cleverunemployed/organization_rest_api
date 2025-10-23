"""Initial migration

Revision ID: 7d658a69d1ad
Revises: 94528eb8c915
Create Date: 2025-10-23 16:02:43.838069

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d658a69d1ad'
down_revision: Union[str, Sequence[str], None] = '94528eb8c915'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
