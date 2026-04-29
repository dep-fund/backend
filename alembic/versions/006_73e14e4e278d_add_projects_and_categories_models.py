"""add projects and categories models

Revision ID: 73e14e4e278d
Revises: e2a95be6396e
Create Date: 2026-04-29 19:24:41.843710

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '73e14e4e278d'
down_revision: Union[str, Sequence[str], None] = 'e2a95be6396e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    project_state_enum = sa.Enum(
        'PENDING', 'APPROVED', 'CANCELED',
        name='project_state'
    )
    
    op.create_table('CATEGORY',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_CATEGORY')),
    sa.UniqueConstraint('name', name=op.f('uq_CATEGORY_name'))
    )
    op.create_table('PROJECT',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('total_amount', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('state', project_state_enum, nullable=False, server_default='PENDING'),
    sa.Column('ubication', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['USER.id'], name=op.f('fk_PROJECT_user_id_USER')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_PROJECT'))
    )
    op.create_table('CATEGORY_PROJECT',
    sa.Column('project_id', sa.UUID(), nullable=False),
    sa.Column('category_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['CATEGORY.id'], name=op.f('fk_CATEGORY_PROJECT_category_id_CATEGORY')),
    sa.ForeignKeyConstraint(['project_id'], ['PROJECT.id'], name=op.f('fk_CATEGORY_PROJECT_project_id_PROJECT')),
    sa.PrimaryKeyConstraint('project_id', 'category_id', name=op.f('pk_CATEGORY_PROJECT'))
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('CATEGORY_PROJECT')
    op.drop_table('PROJECT')
    op.drop_table('CATEGORY')
    sa.Enum(name='project_state').drop(op.get_bind())