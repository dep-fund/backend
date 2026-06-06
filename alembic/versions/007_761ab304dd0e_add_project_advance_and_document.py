"""add project advance and document

Revision ID: 761ab304dd0e
Revises: 73e14e4e278d
Create Date: 2026-05-06 20:36:57.941203

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '761ab304dd0e'
down_revision: Union[str, Sequence[str], None] = '73e14e4e278d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('PROJECT_ADVANCE',
    sa.Column('project_id', sa.UUID(), nullable=False),
    sa.Column('number', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=500), nullable=False),
    sa.Column('url', sa.String(length=500), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['PROJECT.id'], name=op.f('fk_PROJECT_ADVANCE_project_id_PROJECT')),
    sa.PrimaryKeyConstraint('project_id', 'number', name=op.f('pk_PROJECT_ADVANCE'))
    )
    op.create_table('PROJECT_DOCUMENT',
    sa.Column('project_id', sa.UUID(), nullable=False),
    sa.Column('number', sa.Integer(), nullable=False),
    sa.Column('url', sa.String(length=500), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['PROJECT.id'], name=op.f('fk_PROJECT_DOCUMENT_project_id_PROJECT')),
    sa.PrimaryKeyConstraint('project_id', 'number', name=op.f('pk_PROJECT_DOCUMENT'))
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('PROJECT_DOCUMENT')
    op.drop_table('PROJECT_ADVANCE')
