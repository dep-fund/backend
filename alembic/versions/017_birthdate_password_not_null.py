"""birthdate not null

Revision ID: 5e86901756f8
Revises: e27183c4a1c5
Create Date: 2026-06-26 20:13:26.202669

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5e86901756f8"
down_revision: Union[str, Sequence[str], None] = "e27183c4a1c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Set a default for existing null birthdates before making NOT NULL
    op.execute("UPDATE \"USER\" SET birthdate = '2000-01-01' WHERE birthdate IS NULL")
    op.alter_column("USER", "birthdate", existing_type=sa.DATE(), nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("USER", "birthdate", existing_type=sa.DATE(), nullable=True)
