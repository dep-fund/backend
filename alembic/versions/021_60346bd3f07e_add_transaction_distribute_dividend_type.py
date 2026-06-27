"""add transaction distribute dividend type

Revision ID: 60346bd3f07e
Revises: 36abc6542739
Create Date: 2026-06-27 02:06:56.890204

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "60346bd3f07e"
down_revision: Union[str, Sequence[str], None] = "36abc6542739"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "ALTER TYPE transaction_type ADD VALUE IF NOT EXISTS 'DIVIDEND_DISTRIBUTION'"
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
