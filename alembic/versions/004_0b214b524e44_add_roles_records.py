"""add roles records

Revision ID: 0b214b524e44
Revises: 7eba65c2c7ab
Create Date: 2026-04-18 19:48:06.357854

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0b214b524e44'
down_revision: Union[str, Sequence[str], None] = '7eba65c2c7ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        INSERT INTO "ROLE" (id, type)
        SELECT gen_random_uuid(), 'ADMIN'
        WHERE NOT EXISTS (
            SELECT 1 FROM "ROLE" WHERE type = 'ADMIN'
        );

        INSERT INTO "ROLE" (id, type)
        SELECT gen_random_uuid(), 'STANDARD'
        WHERE NOT EXISTS (
            SELECT 1 FROM "ROLE" WHERE type = 'STANDARD'
        );
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        DELETE FROM "ROLE"
        WHERE type IN ('ADMIN', 'STANDARD');
    """)
