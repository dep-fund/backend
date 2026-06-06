"""add user table

Revision ID: 77f4426767ca
Revises: 
Create Date: 2026-04-15 23:49:30.420910

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '77f4426767ca'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('USER',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=100), nullable=False),
    sa.Column('image', sa.String(length=255), nullable=True),
    sa.Column('activated', sa.Boolean(), nullable=False, server_default=sa.true()),
    sa.Column('blocked', sa.Boolean(), nullable=False, server_default=sa.false()),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_USER')),
    sa.UniqueConstraint('email', name=op.f('uq_USER_email')),
    sa.UniqueConstraint('username', name=op.f('uq_USER_username'))
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('USER')
