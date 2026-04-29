"""add oauth

Revision ID: e2a95be6396e
Revises: 0b214b524e44
Create Date: 2026-04-27 18:49:54.764354

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2a95be6396e'
down_revision: Union[str, Sequence[str], None] = '0b214b524e44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    auth_provider_enum = sa.Enum('LOCAL', 'GOOGLE', name='auth_provider_type')
    auth_provider_enum.create(op.get_bind())
    
    op.add_column('USER', sa.Column('google_id', sa.String(length=255), nullable=True))
    op.add_column('USER', sa.Column('auth_provider', auth_provider_enum, nullable=False, server_default='LOCAL'))
    op.alter_column('USER', 'password',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.String(length=255),
               nullable=True)
    op.create_unique_constraint(op.f('uq_USER_google_id'), 'USER', ['google_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f('uq_USER_google_id'), 'USER', type_='unique')
    op.alter_column('USER', 'password',
               existing_type=sa.String(length=255),
               type_=sa.VARCHAR(length=100),
               nullable=False)
    op.drop_column('USER', 'auth_provider')
    op.drop_column('USER', 'google_id')
    sa.Enum(name='auth_provider_type').drop(op.get_bind())