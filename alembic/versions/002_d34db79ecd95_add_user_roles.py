"""add user roles

Revision ID: d34db79ecd95
Revises: 77f4426767ca
Create Date: 2026-04-17 17:30:30.108367

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd34db79ecd95'
down_revision: Union[str, Sequence[str], None] = '77f4426767ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE TYPE user_type AS ENUM ('STANDARD', 'ADMIN')")
    op.create_table('ADMIN_USER',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['USER.id'], name=op.f('fk_ADMIN_USER_id_USER')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_ADMIN_USER'))
    )
    op.create_table('STANDARD_USER',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['USER.id'], name=op.f('fk_STANDARD_USER_id_USER')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_STANDARD_USER'))
    )
    op.add_column('USER', sa.Column('name', sa.String(length=100), nullable=False))
    op.add_column('USER', sa.Column('last_name', sa.String(length=100), nullable=False))
    op.add_column('USER', sa.Column('birthdate', sa.Date(), nullable=True))
    op.add_column('USER', sa.Column('type', sa.Enum('STANDARD', 'ADMIN', name='user_type'), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('USER', 'type')
    op.drop_column('USER', 'birthdate')
    op.drop_column('USER', 'last_name')
    op.drop_column('USER', 'name')
    op.drop_table('STANDARD_USER')
    op.drop_table('ADMIN_USER')
    op.execute("DROP TYPE user_type")
