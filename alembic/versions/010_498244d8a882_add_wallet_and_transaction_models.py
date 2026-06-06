"""add wallet and transaction models

Revision ID: 498244d8a882
Revises: edf84e112673
Create Date: 2026-06-03 01:06:30.132936

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "498244d8a882"
down_revision: Union[str, Sequence[str], None] = "edf84e112673"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "WALLET",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("address", sa.String(length=100), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["STANDARD_USER.id"],
            name=op.f("fk_WALLET_user_id_STANDARD_USER"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_WALLET")),
        sa.UniqueConstraint("address", name=op.f("uq_WALLET_address")),
    )
    op.create_table(
        "TRANSACTION",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tx_hash", sa.String(length=66), nullable=False),
        sa.Column(
            "type",
            sa.Enum("BUY", "SELL", "DIVIDEND", "INVESTMENT", name="transaction_type"),
            nullable=False,
        ),
        sa.Column("wallet_id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["PROJECT.id"],
            name=op.f("fk_TRANSACTION_project_id_PROJECT"),
        ),
        sa.ForeignKeyConstraint(
            ["wallet_id"], ["WALLET.id"], name=op.f("fk_TRANSACTION_wallet_id_WALLET")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_TRANSACTION")),
        sa.UniqueConstraint("tx_hash", name=op.f("uq_TRANSACTION_tx_hash")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("TRANSACTION")
    op.drop_table("WALLET")
