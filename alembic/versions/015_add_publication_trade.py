"""add publication and trade models

Revision ID: a1b2c3d4e5f6
Revises: bc1aee3d1d65
Create Date: 2026-06-17 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "bc1aee3d1d65"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "PUBLICATION",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("token_id", sa.UUID(), nullable=False),
        sa.Column("seller_id", sa.UUID(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("active", "completed", "canceled", name="publication_status"),
            nullable=False,
        ),
        sa.Column("total", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("available", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("price_per_token", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["token_id"], ["TOKEN.id"], name=op.f("fk_PUBLICATION_token_id_TOKEN")
        ),
        sa.ForeignKeyConstraint(
            ["seller_id"], ["USER.id"], name=op.f("fk_PUBLICATION_seller_id_USER")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_PUBLICATION")),
    )

    op.create_table(
        "TRADE",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("publication_id", sa.UUID(), nullable=False),
        sa.Column("buyer_id", sa.UUID(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("total_price", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "confirmed", "failed", name="trade_status"),
            nullable=False,
        ),
        sa.Column("tx_hash", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["publication_id"],
            ["PUBLICATION.id"],
            name=op.f("fk_TRADE_publication_id_PUBLICATION"),
        ),
        sa.ForeignKeyConstraint(
            ["buyer_id"], ["USER.id"], name=op.f("fk_TRADE_buyer_id_USER")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_TRADE")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("TRADE")
    op.drop_table("PUBLICATION")
    op.execute("DROP TYPE IF EXISTS trade_status")
    op.execute("DROP TYPE IF EXISTS publication_status")