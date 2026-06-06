"""add token model

Revision ID: bc1aee3d1d65
Revises: ec4a7326d0f2
Create Date: 2026-06-04 20:26:30.588082

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "bc1aee3d1d65"
down_revision: Union[str, Sequence[str], None] = "ec4a7326d0f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "TOKEN",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("suffix", sa.String(length=10), nullable=False),
        sa.Column("contract_address", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_TOKEN")),
        sa.UniqueConstraint("contract_address", name=op.f("uq_TOKEN_contract_address")),
        sa.UniqueConstraint("name", name=op.f("uq_TOKEN_name")),
        sa.UniqueConstraint("suffix", name=op.f("uq_TOKEN_suffix")),
    )
    op.create_table(
        "TOKEN_PROJECT",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("token_id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("total_supply", sa.Numeric(precision=20, scale=0), nullable=False),
        sa.Column(
            "available_supply", sa.Numeric(precision=20, scale=0), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["PROJECT.id"],
            name=op.f("fk_TOKEN_PROJECT_project_id_PROJECT"),
        ),
        sa.ForeignKeyConstraint(
            ["token_id"], ["TOKEN.id"], name=op.f("fk_TOKEN_PROJECT_token_id_TOKEN")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_TOKEN_PROJECT")),
        sa.UniqueConstraint("project_id", name=op.f("uq_TOKEN_PROJECT_project_id")),
    )
    op.add_column(
        "PROJECT", sa.Column("estimated_development_days", sa.Integer(), nullable=True)
    )
    op.add_column(
        "PROJECT", sa.Column("dividend_address", sa.String(length=255), nullable=True)
    )
    op.add_column(
        "PROJECT", sa.Column("offering_address", sa.String(length=255), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("PROJECT", "offering_address")
    op.drop_column("PROJECT", "dividend_address")
    op.drop_column("PROJECT", "estimated_development_days")
    op.drop_table("TOKEN_PROJECT")
    op.drop_table("TOKEN")
