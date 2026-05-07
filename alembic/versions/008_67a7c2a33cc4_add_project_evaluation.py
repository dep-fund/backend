"""add project evaluation

Revision ID: 67a7c2a33cc4
Revises: 761ab304dd0e
Create Date: 2026-05-06 21:38:40.327340

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '67a7c2a33cc4'
down_revision: Union[str, Sequence[str], None] = '761ab304dd0e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "ALTER TYPE project_state ADD VALUE IF NOT EXISTS 'REJECTED'"
    )

    project_state_enum = postgresql.ENUM(
        'PENDING',
        'APPROVED',
        'CANCELED',
        'REJECTED',
        name='project_state',
        create_type=False
    )
    
    op.create_table('EVALUATED_BY',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('project_id', sa.UUID(), nullable=False),
    sa.Column('admin_id', sa.UUID(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('state', project_state_enum, nullable=False),
    sa.Column('date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['admin_id'], ['ADMIN_USER.id'], name=op.f('fk_EVALUATED_BY_admin_id_ADMIN_USER')),
    sa.ForeignKeyConstraint(['project_id'], ['PROJECT.id'], name=op.f('fk_EVALUATED_BY_project_id_PROJECT')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_EVALUATED_BY'))
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('EVALUATED_BY')
