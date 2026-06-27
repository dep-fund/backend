"""add token_id, source, is_active to investment

Revision ID: 2388c1fdae77
Revises: 615808ece96b
Create Date: 2026-06-26 19:27:00.716164

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2388c1fdae77'
down_revision: Union[str, Sequence[str], None] = '615808ece96b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

investment_source_enum = sa.Enum(
    "offering", "marketplace", name="investment_source"
)


def upgrade() -> None:
    """Upgrade schema."""
    # Crear el tipo enum ANTES de usarlo en la columna
    investment_source_enum.create(op.get_bind(), checkfirst=True)

    op.add_column('INVESTMENT', sa.Column('token_id', sa.UUID(), nullable=False))
    op.add_column('INVESTMENT', sa.Column('source', investment_source_enum, nullable=False))
    op.add_column('INVESTMENT', sa.Column('is_active', sa.Boolean(), nullable=False))
    op.add_column('INVESTMENT', sa.Column('tx_hash', sa.String(length=255), nullable=True))
    op.create_foreign_key(op.f('fk_INVESTMENT_token_id_TOKEN'), 'INVESTMENT', 'TOKEN', ['token_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f('fk_INVESTMENT_token_id_TOKEN'), 'INVESTMENT', type_='foreignkey')
    op.drop_column('INVESTMENT', 'tx_hash')
    op.drop_column('INVESTMENT', 'is_active')
    op.drop_column('INVESTMENT', 'source')
    op.drop_column('INVESTMENT', 'token_id')

    # Borrar el tipo enum al final, una vez que ninguna columna lo usa
    investment_source_enum.drop(op.get_bind(), checkfirst=True)