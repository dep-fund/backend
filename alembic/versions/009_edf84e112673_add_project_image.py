"""add project image

Revision ID: edf84e112673
Revises: 67a7c2a33cc4
Create Date: 2026-05-28 13:31:39.139933

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "edf84e112673"
down_revision: Union[str, Sequence[str], None] = "67a7c2a33cc4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "PROJECT_IMAGE",
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("public_id", sa.String(length=500), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["PROJECT.id"],
            name=op.f("fk_PROJECT_IMAGE_project_id_PROJECT"),
        ),
        sa.PrimaryKeyConstraint("project_id", "number", name=op.f("pk_PROJECT_IMAGE")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("PROJECT_IMAGE")
