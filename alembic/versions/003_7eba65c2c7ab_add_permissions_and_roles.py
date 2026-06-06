"""add permissions and roles

Revision ID: 7eba65c2c7ab
Revises: d34db79ecd95
Create Date: 2026-04-17 23:32:58.787409

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7eba65c2c7ab'
down_revision: Union[str, Sequence[str], None] = 'd34db79ecd95'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('PERMISSION',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('type', sa.String(length=100), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_PERMISSION')),
    sa.UniqueConstraint('type', name=op.f('uq_PERMISSION_type'))
    )
    op.create_table('ROLE',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('type', sa.String(length=100), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_ROLE')),
    sa.UniqueConstraint('type', name=op.f('uq_ROLE_type'))
    )
    op.create_table('PERMISSION_ROLE',
    sa.Column('role_id', sa.UUID(), nullable=False),
    sa.Column('permission_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['permission_id'], ['PERMISSION.id'], name=op.f('fk_PERMISSION_ROLE_permission_id_PERMISSION')),
    sa.ForeignKeyConstraint(['role_id'], ['ROLE.id'], name=op.f('fk_PERMISSION_ROLE_role_id_ROLE')),
    sa.PrimaryKeyConstraint('role_id', 'permission_id', name=op.f('pk_PERMISSION_ROLE'))
    )
    op.add_column('USER', sa.Column('role_id', sa.UUID(), nullable=False))
    op.create_foreign_key(op.f('fk_USER_role_id_ROLE'), 'USER', 'ROLE', ['role_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f('fk_USER_role_id_ROLE'), 'USER', type_='foreignkey')
    op.drop_column('USER', 'role_id')
    op.drop_table('PERMISSION_ROLE')
    op.drop_table('ROLE')
    op.drop_table('PERMISSION')
